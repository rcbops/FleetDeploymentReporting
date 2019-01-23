"use strict";

function ReportTableViewController() {
    var self = this;

    var emptyRow = '<tr></tr>';
    var emptyHead = '<th></th>';
    var emptyCell = '<td></td>';
    var emptyTable = '<tr><td>No Matching Results</td></tr>';

    var thead = $('#renderTable thead');
    var tbody = $('#renderTable tbody');

    self.$onInit = function() {
        self.render();
    };

    // Build html report table using jquery
    self.render = function() {
        // Empty the table
        thead.html("");
        tbody.html("");

        // Check data
        if (self.data.length < 1) {
            var empty = $(emptyTable);
            tbody.append(empty);
            return;
        }

        // Build column headers row
        var headers = Object.keys(self.data[0])
        var tr = $(emptyRow);
        angular.forEach(headers, function(header) {
            var th = $(emptyHead).text(header);
            tr.append(th);
        });
        thead.append(tr);

        // Build rows
        angular.forEach(self.data, function(row) {
            var tr = $(emptyRow);
            angular.forEach(headers, function(header) {
                var td = $(emptyCell).text(row[header]);
                tr.append(td);
            });
            tbody.append(tr);
        });
    };
}

angular.module('cloudSnitch').component('reporttableview', {
    templateUrl: '/static/web/html/reports/tableview.html',
    controller: [ReportTableViewController],
    bindings: {
        data: '<'
    }
});


function ReportForceDiagramViewController() {

    var self = this;
    self.nodeCounts = [100, 250, 500, 1000];

    self.linkDistanceMin = 10;
    self.linkDistanceMax = 200;
    self.linkDistanceStep = 10;

    self.chargeMin = 10;
    self.chargeMax = 200;
    self.chargeStep = 10;

    self.radiusMin = 5;
    self.radiusMax = 30;
    self.radiusStep = 1;

    const colorScale = d3.scaleOrdinal(d3.schemeCategory10);

    /**
     * Transform report json into usable force diagram data.
     */
    function prepareData(data, maxNodes) {
        const prepared = {
            nodes: [],
            links: []
        };

        const nodeMap = {};

        // Pull list of columns from first object in data
        const fields = (data.length > 0) ? Object.keys(data[0]) : {};

        // Iterate over each row.
        var row = 0;
        while (row < data.length && prepared.nodes.length < maxNodes) {

            // Iterate over each field.
            var field = 0;
            while (field < fields.length && prepared.nodes.length < maxNodes) {
                var nodeId = data[row][fields[field]];

                // Update the count of the node if already exists
                if (nodeId in nodeMap) {
                    nodeMap[nodeId].count++;

                // Create the node if it does not exist
                } else {
                    var newNode = {
                        id: nodeId,
                        color: colorScale(field),
                        count: 1
                    }
                    prepared.nodes.push(newNode);
                    nodeMap[nodeId] = newNode;
                }

                // Create a new link if not first field.
                if (field != 0) {
                    var newLink = {
                        source: data[row][fields[field - 1]],
                        target: nodeId
                    };
                    if (newLink.source != newLink.target) {
                        prepared.links.push(newLink);
                    }
                }
                field++;
            }
            row++;
        }
        return prepared;
    }

    /**
     * For dragging nodes in the visualization.
     */
    function drag(simulation) {
        function dragStarted(d) {
            if (!d3.event.active) {
                simulation.alphaTarget(0.3).restart();
            }
            d.fx = d.x;
            d.fy = d.y;
        }

        function dragged(d) {
            d.fx = d3.event.x;
            d.fy = d3.event.y;
        }

        function dragEnded(d) {
            if (!d3.event.active) {
                simulation.alphaTarget(0);
            }
            d.fx = null;
            d.fy = null;
        }

        return d3.drag()
            .on("start", dragStarted)
            .on("drag", dragged)
            .on("end", dragEnded)
    }

    /**
     * Adjust center force. Should be done on start and on resize.
     */
    function updateCenter() {
        const width = parseInt(self.svg.style('width'));
        const height = parseInt(self.svg.style('height'));
        self.simulation.force('center', d3.forceCenter(width / 2, height / 2));
        self.simulation.alpha(1).restart();
    }

    /**
     * Handle zoom events on visualization.
     */
    function zoom() {
        self.svg
            .select("g.all")
            .attr('transform', d3.event.transform);
    }

    /**
     * Toggles display of controls.
     */
    self.toggleControls = function() {
        self.toggleCtrls = !self.toggleCtrls;
    };


    /**
     * Adjust the link distance between nodes.
     */
    self.setLinkDistance = function() {
        self.simulation.force('link').distance(self.linkDistance);
        self.simulation.alpha(1).restart();
    };

    /**
     * Adjust the charge between nodes.
     */
    self.setCharge = function() {
        self.simulation.force('charge').strength(-self.charge);
        self.simulation.alpha(1).restart();
    };

    /**
     * Adjust the radius of nodes.
     */
    self.setRadius = function() {
        self.svg.selectAll("circle").attr("r", self.radius);
    };

    /**
     * Refactor data to account for self.maxNodes.
     * Also clears old links and nodes.
     */
    self.updateData = function() {
        self.prepared = prepareData(self.data, self.maxNodes);
        self.simulation.nodes(self.prepared.nodes);
        self.simulation.force('link', d3.forceLink(self.prepared.links).id(d => d.id).distance(self.linkDistance));

        self.svg.selectAll(".links line").remove();
        var linkData = self.svg.select("g.links").selectAll("line").data(self.prepared.links);
        linkData.enter()
            .append('line')

        self.svg.selectAll(".nodes circle").remove();
        var nodeData = self.svg.select("g.nodes").selectAll("circle").data(self.prepared.nodes)
        nodeData.enter()
            .append("circle")
                .attr("r", self.radius)
                .attr("fill", d => d.color)
                .call(drag(self.simulation))
                .append('title').text(d => d.id)

        // Restart the simulation
        self.simulation.alpha(1).restart();
    };


    self.$onInit = function() {
        self.maxNodes = self.maxNodes || 500;
        self.radius = self.radius || 12;
        self.linkDistance = self.linkDistance || 70;
        self.charge = self.charge || 70;
        self.toggleCtrls = false;

        self.svg = d3.select('svg#forcediagram');

        self.simulation = d3.forceSimulation();
        updateCenter();

        //self.updateCharge();
        self.simulation.force('charge', d3.forceManyBody().strength(-self.charge));

        // Append container for everything for zoom
        var g = self.svg.append('g').attr('class', 'all');

        // Add zoom behaviour
        d3.zoom().on('zoom', zoom)(self.svg);

        // Append container for links
        g.append('g')
            .attr('class', 'links')
            .attr('stroke', '#999')
            .attr('stroke-opacity', 0.6)
            .attr('stroke-width', 3);

        // Append container for nodes
        g.append('g')
            .attr('class', 'nodes')
            .attr('stroke', '#fff')
            .attr('stroke-width', 1.5)

        // Add behaviour to adjust positions of lines and circles on each tick
        self.simulation.on("tick", () => {
            d3.selectAll('g.links line')
                .attr("x1", d => d.source.x)
                .attr("y1", d => d.source.y)
                .attr("x2", d => d.target.x)
                .attr("y2", d => d.target.y);

            d3.selectAll('g.nodes circle')
                .attr("cx", d => d.x)
                .attr("cy", d => d.y);
        });

        window.addEventListener('resize', updateCenter);
        self.updateData();
    };

    /**
     * Remove window listeners created during $onInit
     */
    self.$onDestroy = function() {
        window.removeEventListener('resize', updateCenter);
    };
}

angular.module('cloudSnitch').component('reportforcediagramview', {
    templateUrl: '/static/web/html/reports/forcediagramview.html',
    controller: [ReportForceDiagramViewController],
    bindings: {
        data: '<'
    }
});

/**
 * Controller for pie chart visualization.
 */
function ReportPieChartViewController() {

    var self = this;

    /**
     * Convert array of javascript objects into data suitable for
     * the pie chart component.
     */
    function prepareData(column) {

        var groupedData = d3.nest()
            .key(d => d[column])
            .rollup(d => d.length)
            .entries(self.data);

        var groupedObjs = [];
        angular.forEach(groupedData, function(v) {
            groupedObjs.push({
                label: v.key,
                value: v.value,
            });
        });

        groupedObjs.sort(function(a, b) {
            return d3.descending(a.value, b.value);
        });
        return groupedObjs;
    }

    self.$onInit = function() {
        // Return early if empty data
        if (self.data.length < 1) { return; }
        // Determine columns from first item in array
        const columns = (self.data.length > 0) ? Object.keys(self.data[0]) : null;
        self.charts = [];
        for (var i = 0; i < columns.length; i++) {
            self.charts.push({
                title: columns[i],
                data: prepareData(columns[i])
            });
        }
    };
}

angular.module('cloudSnitch').component('reportpiechartview', {
    templateUrl: '/static/web/html/reports/piechartview.html',
    controller: [ReportPieChartViewController],
    bindings: {
        data: '<'
    }
});

function ReportRenderController() {
    var self = this;

    self.views = [
        {
            id: "table",
            label: "Table"
        },
        {
            id: "forceDiagram",
            label: "Force Diagram"
        },
        {
            id: "pieChart",
            label: "Pie Chart"
        }
    ];

    self.$onInit = function() {
        self.view = self.view || self.views[0];
    };
}


angular.module('cloudSnitch').component('reportrender', {
    templateUrl: '/static/web/html/reports/render.html',
    controller: [ReportRenderController],
    bindings: {
        data: '<'
    }
});
