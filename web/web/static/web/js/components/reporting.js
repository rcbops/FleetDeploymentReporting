function ReportTableViewController() {
    var self = this;

    var emptyRow = "<tr></tr>";
    var emptyHead = "<th></th>";
    var emptyCell = "<td></td>";
    var emptyTable = "<tr><td>No Matching Results</td></tr>";

    var thead = $("#renderTable thead");
    var tbody = $("#renderTable tbody");

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
        var headers = Object.keys(self.data[0]);
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

angular.module("cloudSnitch").component("reporttableview", {
    templateUrl: "/static/web/html/reports/tableview.html",
    controller: [ReportTableViewController],
    bindings: {
        data: "<"
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
                    };
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
            .on("end", dragEnded);
    }

    /**
     * Adjust center force. Should be done on start and on resize.
     */
    function updateCenter() {
        const width = parseInt(self.svg.style("width"));
        const height = parseInt(self.svg.style("height"));
        self.simulation.force("center", d3.forceCenter(width / 2, height / 2));
        self.simulation.alpha(1).restart();
    }

    /**
     * Handle zoom events on visualization.
     */
    function zoom() {
        self.svg
            .select("g.all")
            .attr("transform", d3.event.transform);
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
        self.simulation.force("link").distance(self.linkDistance);
        self.simulation.alpha(1).restart();
    };

    /**
     * Adjust the charge between nodes.
     */
    self.setCharge = function() {
        self.simulation.force("charge").strength(-self.charge);
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
        self.simulation.force("link", d3.forceLink(self.prepared.links).id(d => d.id).distance(self.linkDistance));

        self.svg.selectAll(".links line").remove();
        var linkData = self.svg.select("g.links").selectAll("line").data(self.prepared.links);
        linkData.enter()
            .append("line");

        self.svg.selectAll(".nodes circle").remove();
        var nodeData = self.svg.select("g.nodes").selectAll("circle").data(self.prepared.nodes);
        nodeData.enter()
            .append("circle")
            .attr("r", self.radius)
            .attr("fill", d => d.color)
            .call(drag(self.simulation))
            .append("title").text(d => d.id);

        // Restart the simulation
        self.simulation.alpha(1).restart();
    };


    self.$onInit = function() {
        self.maxNodes = self.maxNodes || 500;
        self.radius = self.radius || 12;
        self.linkDistance = self.linkDistance || 70;
        self.charge = self.charge || 70;
        self.toggleCtrls = false;

        self.svg = d3.select("svg#forcediagram");

        self.simulation = d3.forceSimulation();
        updateCenter();

        //self.updateCharge();
        self.simulation.force("charge", d3.forceManyBody().strength(-self.charge));

        // Append container for everything for zoom
        var g = self.svg.append("g").attr("class", "all");

        // Add zoom behaviour
        d3.zoom().on("zoom", zoom)(self.svg);

        // Append container for links
        g.append("g")
            .attr("class", "links")
            .attr("stroke", "#999")
            .attr("stroke-opacity", 0.6)
            .attr("stroke-width", 3);

        // Append container for nodes
        g.append("g")
            .attr("class", "nodes")
            .attr("stroke", "#fff")
            .attr("stroke-width", 1.5);

        // Add behaviour to adjust positions of lines and circles on each tick
        self.simulation.on("tick", () => {
            d3.selectAll("g.links line")
                .attr("x1", d => d.source.x)
                .attr("y1", d => d.source.y)
                .attr("x2", d => d.target.x)
                .attr("y2", d => d.target.y);

            d3.selectAll("g.nodes circle")
                .attr("cx", d => d.x)
                .attr("cy", d => d.y);
        });

        window.addEventListener("resize", updateCenter);
        self.updateData();
    };

    /**
     * Remove window listeners created during $onInit
     */
    self.$onDestroy = function() {
        window.removeEventListener("resize", updateCenter);
    };
}

angular.module("cloudSnitch").component("reportforcediagramview", {
    templateUrl: "/static/web/html/reports/forcediagramview.html",
    controller: [ReportForceDiagramViewController],
    bindings: {
        data: "<"
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

angular.module("cloudSnitch").component("reportpiechartview", {
    templateUrl: "/static/web/html/reports/piechartview.html",
    controller: [ReportPieChartViewController],
    bindings: {
        data: "<"
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


angular.module("cloudSnitch").component("reportrender", {
    templateUrl: "/static/web/html/reports/render.html",
    controller: [ReportRenderController],
    bindings: {
        data: "<"
    }
});


function ReportingController($scope, $location, reportsService, cloudSnitchApi, messagingService, paramService) {

    var self = this;

    const generic = "Generic";
    const queryParams = {
        name: "name",
        parameters: "parameters"
    };

    /**
     * Set selected report on report list change.
     *
     * If a report has not been selected, select the report indicated by
     *     query params.
     * If not indicated by query params, select the
     *     generic report.
     * If the generic report cannot be found, default to the first report.
     */
    function handleReportsChange() {
        var i;
        var newReport;
        var target = self.name || generic;
        // Default to the generic report
        if (self.report === null) {
            for (i = 0; i < self.reports.length; i++) {
                if (self.reports[i].name == target) {
                    newReport = self.reports[i];
                    break;
                }
            }
            // Default to the first report if generic not found.
            self.report = newReport || self.reports[0];
            self.changeReport();
        }
    }

    /**
     * Make the query params in address bar match.
     */
    function syncLocation() {
        self.name = self.report.name;
        $location.search(queryParams.name, self.name);
        paramService.search(queryParams.parameters, self.parameters);
    }

    /**
     * Init state
     */
    self.$onInit = function() {
        self.serverErrors = null;
        self.showJsonParams = false;
        self.data = null;

        self.report = null;

        // Check location for report name
        self.name = $location.search()[queryParams.name] || null;

        // Check location for parameters
        self.parameters = paramService.search(queryParams.parameters) || {};

        self.busy = false;

        self.reports = reportsService.reports;
        if (self.reports.length > 0) {
            handleReportsChange();
        }

        // Set loading if reports not loaded yet
        self.reportsLoading = (self.reports.length == 0);
    };

    /**
     * Scrub report query params from $location
     */
    self.$onDestroy = function() {
        angular.forEach(queryParams, function(v) {
            paramService.search(v, null);
        });
    };

    /**
     * Filter out inputs that are no longer necessary
     */
    self.changeReport = function() {
        var key;
        var newItems = self.report.form_data.map(function(item) {
            return item.name;
        });
        for (key in self.parameters) {
            if (!newItems.includes(key)) {
                delete self.parameters[key];
            }
        }
        // Sync existing parameters with report form data
        syncLocation();
    };

    /**
     * Listen for list change events.
     */
    $scope.$on("reports:update", function() {
        self.reports = reportsService.reports;
        handleReportsChange();
        self.reportsLoading = false;
    });

    /**
     * Update a report control.
     */
    self.updateControl = function(change) {
        self.parameters[change.name] = change.value;
        syncLocation();
    };

    /**
     * Run the report.
     */
    self.submit = function() {
        var type = "web";
        self.busy = true;
        self.serverErrors = null;

        cloudSnitchApi.runReport(self.report.name, type, self.parameters).then(function(data) {
            self.data = data;
            self.busy = false;
        }, function(resp) {
            self.serverErrors = resp.data;
            self.busy = false;
            messagingService.error(
                "reporting",
                "API ERROR",
                resp.status + " " + resp.statusText
            );
        });
    };

    /**
     * Suggest a file name for report data to download.
     */
    function suggestFileName(type) {
        return self.report.name + "_" + new Date().toISOString() + "." + type;
    }

    /**
     * Download the data as csv or json format.
     */
    self.download = function(type) {

        var blobType, blobStr;

        if (type == "csv") {
            blobType = "text/csv";
            blobStr = Papa.unparse(self.data);
        } else {
            blobType = "application/json";
            blobStr = JSON.stringify(self.data);
        }

        // Create new blob from data
        var blob = new Blob([blobStr], {type: blobType});

        // Create url to blob
        var url = window.URL.createObjectURL(blob);

        // Create a link and simulated click
        var link = angular.element("<a></a>")
            .css("display", "none")
            .attr("href", url)
            .attr("download", suggestFileName(type));
        angular.element("#downloads").append(link);
        link[0].click();

        // Clean up
        link.remove();
        URL.revokeObjectURL(url);
    };

    self.closeRendering = function() {
        self.data = null;
    };

    /**
     * Toggle display of json params use in report api request.
     */
    self.toggleShowJsonParams =  function() {
        self.showJsonParams = !self.showJsonParams;
    };
}

angular.module("cloudSnitch").component("reporting", {
    templateUrl: "/static/web/html/reports/index.html",
    controller: ["$scope", "$location", "reportsService", "cloudSnitchApi", "messagingService", "paramService", ReportingController],
    bindings: {}
});
