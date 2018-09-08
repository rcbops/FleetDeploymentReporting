/**
 * The details controller covers displaying object details.
 */
angular.module('cloudSnitch').controller('DiffController', ['$scope', '$log', '$interval', '$window', 'cloudSnitchApi', 'typesService', 'timeService', function($scope, $log, $interval, $window, cloudSnitchApi, typesService, timeService) {

    var frame = undefined;
    var nodeMap = undefined;
    var nodes = undefined;
    var nodeCount = 0;
    $scope.state = 'loadingStructure';

    $scope.detailNode = undefined;
    $scope.detailNodeType = undefined;
    $scope.detailNodeId = undefined;

    var pollStructure;
    var pollNodes;

    var pollInterval = 3000;
    var nodePageSize = 500;
    var nodeOffset = 0;


    var totalNodes = 0;
    var maxLabelLength = 0;
    var panSpeed = 200;
    var panBoundary = 20;
    var panTimer = null;
    var viewerHeight = null;
    var viewerWidth = null;
    var duration = 750;
    var root;

    var margin = {
        top: 20,
        bottom: 20,
        right: 250,
        left: 250
    }

    var tree = undefined;
    var nodeRadius = 10;

    var svg = undefined;
    var g = undefined;

    var i = 0;


    function zoom() {
        g.attr('transform', d3.event.transform);
    }
    var zoomListener = d3.zoom().scaleExtent([0.1, 3]).on("zoom", zoom);

     // Define the drag listeners for drag/drop behaviour of nodes.
    var dragListener = d3.drag()
        .on("drag", function(d) {
            // get coords of mouseEvent relative to svg container to allow for panning
            relCoords = d3.mouse($('svg#diff').get(0));
            if (relCoords[0] < panBoundary) {
                panTimer = true;
                pan(this, 'left');
            } else if (relCoords[0] > ($('svg#diff').width() - panBoundary)) {

                panTimer = true;
                pan(this, 'right');
            } else if (relCoords[1] < panBoundary) {
                panTimer = true;
                pan(this, 'up');
            } else if (relCoords[1] > ($('svg#diff').height() - panBoundary)) {
                panTimer = true;
                pan(this, 'down');
            } else {
                try {
                    clearTimeout(panTimer);
                } catch (e) {

                }
            }

            d.x0 += d3.event.dy;
            d.y0 += d3.event.dx;
            var node = d3.select(this);
            node.attr("transform", "translate(" + d.y0 + "," + d.x0 + ")");
        });

    function visit(parent, visitFn) {
        if (!parent) return;

        visitFn(parent);

        if (parent.children && parent.children.length) {
            var children = parent.children;
            var count = children.length;
            for (var i = 0; i < count; i++) {
                visit(children[i], visitFn);
            }
        }
    }


    /**
     * Comparison function for sorting siblings in diff tree.
     */
    function siblingCompare(a, b) {
        var d = a.data.model.localeCompare(b.data.model);
        if (d == 0) {
            d = a.data.id.localeCompare(b.data.id);
        }
        return d;
    }

    /**
     * Compute label of a node.
     */
    function label(d) {
        var model = d.model || d.data.model;
        var id = d.id || d.data.id;
        var index = nodeMap[model][id];
        var node = nodes[index];
        var label = model + ": ";
        var labelProp = typesService.diffLabelView[model];
        if (node && angular.isDefined(labelProp))
            label += nodeProp(node, labelProp);
        else
            label += id;
        return label;
    }

    /**
     * Compute size of svg and the tree.
     */
    function sizeTree() {
        var p = svg.select(function() {
            return this.parentNode;
        });
        svg.attr('width', 1);
        svg.attr('height', 1);

        var pNode = p.node();
        var rect = pNode.getBoundingClientRect();
        var style = window.getComputedStyle(pNode);
        var paddingLeft = parseInt(style.getPropertyValue('padding-left'));
        var paddingRight = parseInt(style.getPropertyValue('padding-right'));
        var paddingTop = parseInt(style.getPropertyValue('padding-top'));
        var paddingBottom = parseInt(style.getPropertyValue('padding-bottom'));

        var svgHeight = rect.height - paddingTop - paddingBottom;
        var svgWidth = rect.width - paddingLeft - paddingRight;
        svg.attr('height', svgHeight);
        svg.attr('width', svgWidth);

        var sizeX = svgWidth - margin.right - margin.left;
        var sizeY = svgHeight - margin.bottom - margin.top;
        return {x: sizeX, y: sizeY};
    }

    /**
     * Offset the tree containing "g" element by margin.
     */
    function translateTree() {
        g.attr('transform', 'translate(' + margin.left + ',' + margin.top + ')');
    }

    /**
     * Center view port on a node
     */
    function centerNode(source) {
        t = d3.zoomTransform(svg.node());
        x = -source.y0;
        y = -source.x0;
        x = x * t.k + viewerWidth / 2;
        y = y * t.k + viewerHeight / 2;
        //d3.select('svg').transition()
        svg.transition()
            .duration(duration)
            .call(zoomListener.transform, d3.zoomIdentity.translate(x,y).scale(t.k));
    }

    /**
     * Toggle the children
     */
    function toggleChildren(d) {
        if (d.children) {
            d._children = d.children;
            d.children = null;
        } else if (d._children) {
            d.children = d._children;
            d._children = null;
        }
        return d;
    }

    /**
     * Collapse helper function
     */
    function collapse(d) {
        if (d.children) {
            d._children = d.children;
            d._children.forEach(collapse);
            d.children = null;
        }
    };

    /**
     * Expand helper function
     */
    function expand(d) {
        if (d._children) {
            d.children = d._children;
            d.children.forEach(expand);
            d._children = null;
        }
    }

    /**
     * Toggle children on click
     */
    function click(d) {
        if (d3.event.defaultPrevented) {
             return; // click suppressed
        }
        d = toggleChildren(d);
        update(d);
        centerNode(d);
    }

    /**
     * Creates a curved (diagonal) path from parent to the child nodes
     */
    function diagonal(s, d) {
        path = `M ${s.y} ${s.x}
                C ${(s.y + d.y) / 2} ${s.x},
                  ${(s.y + d.y) / 2} ${d.x},
                  ${d.y} ${d.x}`

        return path
    }

    /**
     * Pan the Tree
     */
    function pan(domNode, direction) {
        var speed = panSpeed;
        if (panTimer) {
            clearTimeout(panTimer);
            translateCorrds = d3.transform(g.attr('transform'));
            if (direction == 'left' || direction == 'right') {
                translateX = direction == 'left' ? translateCoords.translate[0] + speed : translateCoords.translate[0] - speed;
                translateY = translateCoords.translate[1];
            } else if (direction == 'up' || direction == 'down') {
                translateX = translateCoords.translate[0];
                translateY = direction == 'up' ? translateCoords.translate[1] + speed : translateCoords.translate[1] - speed;
            }
            scaleX = translateCoords.scale[0];
            scaleY = translateCoords.scale[1];
            scale = zoomListener.scale();
            g.transition().attr('transform', 'translate(' + translateX + ',' + translateY + ')scale(' + scale + ')');
            d3.select(domNode).select('g.node').attr('transform', 'translate(' + translateX + ',' + translateY + ')');
            zoomListener.scale(zoomListener.scale());
            zoomListener.translate([translateX, translateY]);
            panTimer = setTimeout(function() { pan(domNode, speed, direction); }, 50);
        }
    }

    function render() {
        // Get the svg element
        if (!angular.isDefined(svg)) {
            svg = d3.select('svg#diff');
        }
        svg.call(zoomListener);

        // Make a svg g element if not defined.
        if (!angular.isDefined(g)) {
            g = svg.append('g');
        }
        g.html('');

        s = sizeTree();
        viewerHeight = s.y;
        viewerWidth = s.x;

        // Make the data heirarchy
        if (!angular.isDefined(root)) {
            root = d3.hierarchy(frame);
            root.sort(siblingCompare);
            root.x0 = viewerHeight / 2;
            root.y0 = viewerWidth / 2;
        }

        // Start the tree
        if (!angular.isDefined(tree)) {
            tree = d3.tree();
        }

        // Offset tree for margin
        translateTree();

        // Collapse all children of roots children before rendering.
        root.children.forEach(function(child){
            collapse(child);
        });

        update(root);
        centerNode(root);
    }

    /**
     * Update the tree.
     */
    function update(source) {
        var levelWidth = [1];
        var childCount = function(level, n) {
            if (n.children && n.children.length > 0) {

                if (levelWidth.length <= level + 1) { levelWidth.push(0); }

                levelWidth[level + 1] += n.children.length;
                n.children.forEach(function(d) {
                    childCount(level + 1, d);
                });
            }
        };

        // Visit nodes for count and max label length.
        visit(frame, function(d) {
            totalNodes++;
            maxLabelLength = Math.max(label(d).length, maxLabelLength);
        });

        childCount(0, root);
        var newHeight = d3.max(levelWidth) * 25 // 25 pixels per line
        // Calculate size svg should be.
        // Calcule size tree should be including margin.
        tree.size([newHeight, viewerWidth]);

        // Pass heirarchy to tree
        tree(root);

        // Compute the new layout
        var nodes = root.descendants();
        var links = root.descendants().slice(1);

        // Set widths between levels based on maxLabelLength.
        nodes.forEach(function(d) {
            d.y = (d.depth * (maxLabelLength * 10)); //maxLabelLength * 10px
        });

        var node = g.selectAll(".node")
            .data(nodes, function(d) {
                return d.data.id;
            });

        var nodeEnter = node.enter()
            .append("g")
                .attr("class", function(d) {
                    var classes = 'node';
                    if (d.children)
                        classes += ' node--internal';
                    else
                        classes += ' node--leaf';

                    switch (d.data.side) {
                        case 'left':
                            classes += ' removed';
                            break;
                        case 'right':
                            classes += ' added';
                            break;
                        default:
                            classes += ' unchanged';
                            break;
                    }
                    return classes;
                })
                .attr("transform", function(d) {
                    return "translate(" + source.y0 + "," + source.x0 + ")";
                })
                .on('click', click)
                .on('contextmenu', nodeClickHandler);

        nodeEnter.append("circle")
            .attr("r", nodeRadius)

        nodeEnter.append("text")
            .attr("dy", 3)
            .attr("x", function(d) { return d.children ? -15: 15})
            .style("text-anchor", function(d) { return d.children ? "end": "start"; })
            .style('fill-opacity', 0)
            .text(label);

        // Transition nodes to their new position.
        var nodeUpdate = nodeEnter.merge(node);
        nodeUpdate.transition()
            .duration(duration)
            .attr("transform", function(d) {
                return "translate(" + d.y + "," + d.x + ")";
            });

        nodeUpdate.select("circle")
            .attr("class", function(d) {
                return d._children ? "" : "empty";
            });

        // Fade the text in
        nodeUpdate.select("text")
            .style("fill-opacity", 1);

        var nodeExit = node.exit().transition()
            .duration(duration)
            .attr("transform", function(d) {
                return "translate(" + source.y + "," + source.x + ")";
            })
            .remove();

        nodeExit.select("circle")
            .attr("r", 0);

        nodeExit.select("text")
            .style("fill-opacity", 0);

        var link = g.selectAll(".link")
            .data(links);

        var linkEnter = link.enter()
            .insert('path', 'g')
                .attr('class', 'link')
                .attr('d', function(d) {
                    var o = {x: source.x0, y: source.y0 };
                    return diagonal(o, o);
                });

        var linkUpdate = linkEnter.merge(link);
        linkUpdate.transition()
            .duration(duration)
            .attr('d', function(d) {
                return diagonal(d, d.parent);
            });

        var linkExit = link.exit().transition()
            .duration(duration)
            .attr('d', function(d) {
                var o = {x: source.x, y: source.y};
                return diagonal(o, o);
            })
            .remove();

        nodes.forEach(function(d) {
            d.x0 = d.x;
            d.y0 = d.y;
        });
    }

    function nodeProp(node, prop) {
        if (angular.isDefined(node.both[prop])) { return node.both[prop]; }
        if (angular.isDefined(node.right[prop])) { return node.right[prop]; }
        if (angular.isDefined(node.left[prop])) { return node.left[prop]; }
        return "";
    }

    function updateLabels() {
        if (!angular.isDefined(tree) || !angular.isDefined(root)) { return; }

        var node = g.selectAll(".node")
        node.selectAll("text").text(label);
    };

    function getNodes() {
        var offset = nodeOffset;
        cloudSnitchApi.diffNodes($scope.diff.type, $scope.diff.id, $scope.diff.leftTime, $scope.diff.rightTime, offset, nodePageSize)
        .then(function(result) {
            // Check if the diff tree is finished
            if (!angular.isDefined(result.nodes)) { return; }

            // Check if this is a redundant request.
            if (nodeOffset > offset) { return; }

            // Update the nodes array.
            for (var i = 0; i < result.nodes.length; i++) {
                nodes[offset + i] = result.nodes[i];
            }

            // Update node offset for next polling
            nodeOffset += result.nodes.length;

            // Check if this is the last request
            if (result.nodes.length < nodePageSize) {
                stopPollingNodes();
                // Update labels
                updateLabels();
                $scope.state = 'done';
            }
        }, function(resp) {
            stopPollingNodes();
            $scope.state = 'error';
            $log.log("In promise failure getNodes");
            $scope.$broadcast("notification:api",
                              {
                                 function: "getNodes",
                                 message: resp.statusText,
                                 status: resp.status,
                                 subject: "diffNodes",
                                 type: "ERROR"
                              });
        });
    }

    function nodeClickHandler(d) {
        d3.event.preventDefault();
        var index = nodeMap[d.data.model][d.data.id];
        if (angular.isDefined(index) && nodes[index]) {
            $scope.$apply(function() {
                $scope.detailNodeType = d.data.model;
                $scope.detailNode = nodes[index];
                $scope.detailNodeId = d.data.id;
            });
        }
    }

    /**
     * Stop controller from polling for structure.
     */
    function stopPolling() {
        if (angular.isDefined(pollStructure)) {
            $interval.cancel(pollStructure);
            pollStructure = undefined;
        }
    };

    /**
     * Stop controller for polling for nodes.
     */
    function stopPollingNodes() {
        if (angular.isDefined(pollNodes)) {
            $interval.cancel(pollNodes);
            pollNodes = undefined;
        }
    }

    $scope.humanState = function() {
        switch ($scope.state) {
            case 'empty':
                return 'No meaningful differences.';
            case 'error':
                return 'Error loading diff';
            case 'loadingStructure':
                return 'Loading Structure';
            case 'loadingNodes':
                return 'Loading Nodes';
            case 'done':
                return 'Done';
            default:
                return 'Unknown';
        }
    };

    $scope.detailProps = function() {
        var props = [];
        angular.forEach($scope.detailNode.left, function(value, key) {
            props.push(key);
        });
        angular.forEach($scope.detailNode.right, function(value, key) {
            props.push(key);
        });
        angular.forEach($scope.detailNode.both, function(value, key) {
            props.push(key);
        });
        props = props.filter(function(value, index, self) {
            return self.indexOf(value) === index;
        });
        props.sort();
        return props;
    }

    $scope.detailProp = function(prop, side) {
        var r = {
            val: '',
            css: ''
        }
        if (angular.isDefined($scope.detailNode.both[prop])) {
            r.val = $scope.detailNode.both[prop];
        }
        else {
            r.val = $scope.detailNode[side][prop] || '';
            if (side == 'left')
                r.css = 'diffLeft';
            else
                r.css = 'diffRight';
        }
        return r;
    };

    $scope.closeDetail = function () {
        $scope.detailNode = undefined;
        $scope.detailNodeType = undefined;
        $scope.detailNodeId = undefined;
    }

    function getStructure() {
        cloudSnitchApi.diffStructure($scope.diff.type, $scope.diff.id, $scope.diff.leftTime, $scope.diff.rightTime)
        .then(function(result) {

            if (!angular.isDefined(result.frame)) {
                return;
            }

            stopPolling();

            if (result.frame !== null) {
                $scope.state = 'loadingNodes';
                frame = result.frame;
                nodeMap = result.nodemap;
                nodeCount = result.nodecount;
                nodes = new Array(nodeCount);
                pollNodes = $interval(getNodes, pollInterval);
                render();
            } else {
                $scope.state = 'empty'
                frame = null;
                nodeMap = null;
                nodeCount = 0;
                nodes = [];
            }
        }, function(resp) {
            stopPolling();
            $scope.state = 'error'
            $log.log("In promise failure getStructure");
            $scope.$broadcast("notification:api",
                              {
                                 function: "getStructure",
                                 message: resp.statusText,
                                 status: resp.status,
                                 subject: "diffStructure",
                                 type: "ERROR"
                              });
        });
    }

    $scope.update = function() {
        frame = undefined;
        nodeMap = undefined;
        nodes = undefined;
        nodeCount = 0;
        $scope.state = 'loadingStructure';
        pollStructure = $interval(getStructure, pollInterval);
    };

    $scope.$watch('diff', function(newVal) {
        $scope.update();
    });

    $scope.$on('$destroy', function() {
        stopPolling();
        stopPollingNodes();
    });

    angular.element($window).bind('resize', function() {
        if ($scope.state != 'loadingStructure') {
            render();
            updateLabels();
        }
    });

}]);
