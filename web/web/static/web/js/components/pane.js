/**
 * Controller for pane top controls.
 *   Only registers click events and has
 *   inputs for whether or not a button is clickable.
 */
function PaneTopCtrlController() {
    var self = this;

    /**
     * Register a back event.
     */
    self.back = function() {
        self.onBack({});
    };

    /**
     * Register a diff event.
     */
    self.diff = function() {
        self.onDiff({});
    };

    /**
     * Register a clone event.
     */
    self.clone = function() {
        self.onClone({});
    };

    /**
     * Register a close event.
     */
    self.close = function() {
        self.onClose({});
    };
}

angular.module('cloudSnitch').component('panetopctrl', {
    templateUrl: '/static/web/html/panes/panetopctrl.html',
    controller: [PaneTopCtrlController],
    bindings: {
        backable: '<',
        cloneable: '<',
        diffable: '<',
        onClose: '&',
        onClone: '&',
        onDiff: '&',
        onBack: '&'
    }
});

/**
 * Controller for the panes component.
 *  Handles multiple panes and directs pane to pane communication.
 */
function PanesController(typesService, timeService) {
    var self = this;

    self.$onInit = function() {
        self.maxPanes = self.maxPanes || 2;
        self.panes = [];
        self.diff = undefined;

        // Start with one pane.
        self.add();
    };

    /**
     * Add a pane
     */
    self.add = function() {
        // Return early if adding another pane would exceed max panes
        if (self.panes.length >= self.maxPanes) {
            return true;
        }
        self.panes.push({});
    };

    /**
     * Close a pane.
     */
    self.close = function(index) {
        if (index < self.panes.length) {
            self.panes.splice(index, 1);
        }
    };

    /**
     * Clone a pane
     */
    self.clone = function(frames) {
        if (self.panes.length < self.maxPanes) {
            self.panes.push({frames: frames});
        }
    };

    /**
     * Handle a pane change. example search -> results -> details
     */
    self.paneChange = function(index, frame) {
        self.panes[index].topFrame = frame;
    };

    /**
     * Determine cloneability
     */
    self.cloneable = function() {
        return self.panes.length < self.maxPanes;
    };

    /**
     * Determine if panes are diffable.
     * They must be the same type and on details with the same id.
     */
    self.diffable = function() {
        if (self.panes.length > 1) {
            var a = self.panes[0].topFrame;
            var b = self.panes[1].topFrame;

            if (a === undefined || b === undefined) {
                return false;
            }

            if (a.state != 'details' || b.state != 'details') {
                return false;
            }

            if (a.type != b.type) {
                return false;
            }

            var aId = a.record[a.type][typesService.identityProperty(a.type)];
            var bId = b.record[b.type][typesService.identityProperty(b.type)];
            if (aId != bId) {
                return false;
            }
            return true;
        }
        return false;
    };

    /**
     * Set the diff object to enable the diff view.
     */
    self.showDiff = function() {
        var a = self.panes[0].topFrame;
        var b = self.panes[1].topFrame;
        self.diff = {
            type: a.type,
            id: a.record[a.type][typesService.identityProperty(a.type)],
            leftTime: a.time,
            rightTime: b.time
        };
    };

    /**
     * Handle a diff close.
     */
    self.closeDiff = function() {
        self.diff = undefined;
    }
}

angular.module('cloudSnitch').component('panes', {
    templateUrl: '/static/web/html/panes/panes.html',
    controller: ['typesService', 'timeService', PanesController],
    bindings: {
        maxPanes: '<',
    }
});

/**
 * Pane controller.
 *   Handles state of a pane
 *   Brokers information from frames to the panes component
 *   Brokers information from panes to individual frames.
 */
function PaneController(typesService, timeService) {
    var self = this;

    /**
     * Fires a pane change event to send information up the chain.
     *   Sends a copy of the frame
     */
    function paneChange() {
        self.onPaneChange({
            frame: angular.copy(self.frames[self.frames.length - 1])
        })
    }

    self.$onInit = function() {
        self.cloneable = self.cloneable || false;
        self.diffable = self.diffable || false;
        self.frames = self.frames || [];
        self.id = timeService.str(timeService.now());

        // Add initial frame if None
        if (self.frames.length == 0) {
            self.frames.push({state: 'search'});
        };
        paneChange();
    };

    /**
     * Get the identity value of a frame.
     */
    self.identity = function(index) {
        var frame = self.frames[index];
        var prop = typesService.identityProperty(frame.type);
        return frame.record[frame.type][prop];
    };

    /**
     * Navigate back within the pane, pop a frame off the stack.
     */
    self.back = function() {
        if (self.frames.length > 1) {
            self.frames.splice(-1, 1);
            paneChange();
        }
    };

    /**
     * Mark pane as deleted. The panes component will remove it.
     */
    self.close = function() {
        self.onClose({
            index: self.index
        });
    };

    /**
     * Jump to frame at specified index.
     */
    self.jump = function(index) {
        if (index < self.frames.length) {
            var numSplice = self.frames.length - (index + 1);
            self.frames.splice(index + 1, numSplice);
            paneChange();
        }
    };

    /**
     * Clone this pane. Copy current frames and send to parent.
     */
    self.clone = function() {
        self.onClone({frames: angular.copy(self.frames)});
    };

    /**
     * Trigger the diff view. Pass diff request up to parent.
     */
    self.diff = function() {
        self.onDiff({});
    };

    /**
     * Add a results frame.
     */
    self.results = function(type, time, filters) {
        self.frames.push({
            state: 'results',
            type: type,
            time: time,
            filters: filters
        });
        paneChange();
    };

    /**
     * Add a details frame.
     *   Typically from a row click in results or a child on details.
     */
    self.details = function(record, time, type) {
        self.frames.push({
            state: 'details',
            record: record,
            time: time,
            type: type
        });
        paneChange();
    };

    /**
     * Used to synchronize data with parent component to enable clone and diff.
     */
    self.syncFrame = function(data) {
        var frame = self.frames[self.frames.length - 1];
        angular.extend(frame, data || {});
        paneChange();
    };
}

angular.module('cloudSnitch').component('pane', {
    templateUrl: '/static/web/html/panes/pane.html',
    controller: ['typesService', 'timeService', PaneController],
    bindings: {
        cloneable: '<',
        diffable: '<',
        index: '<',
        frames: '<',
        onClone: '&',
        onClose: '&',
        onDiff: '&',
        onPaneChange: '&'
    }
});

/**
 * Controller for the frame that presents search controls.
 */
function SearchFrameController(typesService, timeService, cloudSnitchApi) {
    var self = this;

    self.typesService = typesService;

    self.$onInit = function() {
        self.path = undefined;
        self.type = self.type || 'Environment';
        self.filters = self.filters || [];

        self.time = self.time;
        if (self.time === undefined) {
            self.setToNow();
        }
        self.updatePath();
    };

    /**
     * Create a default filter.
     */
    self.defaultFilter = function() {
        return {
            model: self.type,
            property: null,
            operator: '=',
            value: null
        };
    };

    /**
     * Add another filter
     */
    self.addFilter = function() {
        self.filters.push(self.defaultFilter());
    };

    /**
     * Remove filter
     */
    self.removeFilter = function(filter) {
        var index = self.filters.indexOf(filter);
        self.filters.splice(index, 1);
    };

    /**
     * Update the current path(path from root type to current type);
     */
    self.updatePath = function() {
        self.path = typesService.path(self.type);
    };

    /**
     * Set time field to now.
     */
    self.setToNow = function() {
        self.time = timeService.str(timeService.now());
    };

    /**
     * Trigger on search event. Notify parent to add a results frame
     */
    self.search = function() {
        self.onSearch({
            type: self.type,
            time: self.time,
            filters: self.filters,
        });
    };

    function syncFrame() {
        self.onSyncFrame({
            data: {
                type: self.type,
                filters: self.filters,
                time: self.time
            }
        });
    }

    /**
     * Sync frame to parent if visible.
     */
    self.$doCheck = function() {
        if (self.focused) {
            syncFrame();
        }
    };
}

angular.module('cloudSnitch').component('searchFrame', {
    templateUrl: '/static/web/html/panes/search.html',
    controller: ['typesService', 'timeService', 'cloudSnitchApi', SearchFrameController],
    bindings: {
        filters: '<',
        focused: '<',
        time: '<',
        type: '<',
        onSearch: '&',
        onSyncFrame: '&'
    }
});

/**
 * Controller for results frame components.
 *  Includes ability to change which fields are displayed.
 *  Includes ability to change sort order and sort field.
 *  Includes abitity to change number of results per page.
 */
function ResultsFrameController(typesService, messagingService, cloudSnitchApi) {
    var self = this;

    self.$onInit = function() {
        self.busy = false;
        self.path = undefined;
        self.records = [];
        self.rows = [];
        self.count = 0;
        self.frameId = 'results_' + Date.now();
        self.headers = [];
        self.showOptions = false;

        self.updatePath();

        // Default paging
        self.page = self.page || 1;
        self.pageSize = self.pageSize || 15;
        self.defaultSizes = [15, 25, 50, 75, 100];
        self.pageSizes = [15];

        // Default fields - should be a function of type
        self.fields = self.fields || self.defaultFields();

        // Default sort order should be first of the fields
        self.sortFieldIndex = self.sortFieldIndex || 0;
        self.sortField = self.fields[self.sortFieldIndex];

        // Default sort direction
        self.sortDirection =  self.sortDirection || 'asc';

        self.setHeaders();

        self.search();
    };

    /**
     * Build list of default fields.
     */
    self.defaultFields = function() {
        var fields = [];
        for (var i = 0; i < self.path.length; i++) {
            var glanceProps = typesService.glanceProperties(self.path[i]);
            for (var j = 0; j < glanceProps.length; j++) {
                fields.push({
                    type: self.path[i],
                    property: glanceProps[j]
                });
            }
        }
        return fields;
    };

    /**
     * Shows/hides the options
     */
    self.toggleOptions = function() {
        self.showOptions = !self.showOptions;
    };

    /**
     * Figure out the path.
     */
    self.updatePath = function() {
        self.path = typesService.path(self.type).slice().reverse();
    };

    /**
     * Create headers for columns in the table.
     */
    self.setHeaders = function() {
        self.headers = [];
        for (var i = 0; i < self.fields.length; i++) {
            self.headers.push("" + self.fields[i].type + "." + self.fields[i].property);
        }
    };

    /**
     * Update rows
     */
    self.updateRows = function() {
        var rows = [];
        angular.forEach(self.records, function(record) {
            var row = [];
            angular.forEach(self.fields, function(field) {
                row.push(record[field.type][field.property]);
            });
            rows.push(row);
        });
        self.rows = rows;
    };

    /**
     * Save current set of records and create a set of rows
     * for use with the paginated table component.
     */
    self.setRecords = function(records) {
        self.records = records
        self.updateRows();
    };

    /**
     * Called when a page is selected.
     */
    self.changePage = function(newPage) {
        self.page = newPage;
        self.search();
    };

    /**
     * Called when control for number of items per page is changed.
     */
    self.changePageSize = function() {
        if (self.pageSize) {
            self.page = 1;
            self.search();
        }
    };

    /**
     * Add a new field. find the first unused property in the reversed path.
     */
    self.addField = function() {
        function fieldToStr(field) {
            return field.type + "_-_" + field.property;
        }

        // Build a set of field representations
        var field;
        var fieldSet = new Set([]);
        for(var i = 0; i < self.fields.length; i++) {
            fieldSet.add(fieldToStr(self.fields[i]));
        }

        // Loop over reversed path types and stop at first field not in set.
        for (var i = 0; i < self.path.length && !field; i++) {
            var type = self.path[i];
            var props = typesService.properties[type];
            for (var j = 0; j < props.length && !field; j++) {
                var f = {type: type, property: props[j]};
                if (!fieldSet.has(fieldToStr(f))) {
                    field = f;
                }
            }
        }

        if (!field) {
            // If an unsed property was not found, use the last property of the last type
            var lastType = self.path[self.path.length - 1];
            var lastProps = typesService.properties[lastType]
            field = {
                type: lastType,
                property: lastProps[lastProps.length - 1]
            };
        }
        self.fields.push(field);
        self.setHeaders();
        self.updateRows();
    };

    /**
     * Called when a field changes
     */
    self.changeField = function(index, field) {
        if (field.type == self.fields[index].type && field.property == self.fields[index].property) {
            return false;
        }

        var oldField = self.fields[index];
        self.fields[index] = field;
        self.setHeaders();

        // Case where the index of the changed field is the sorted field
        if (self.sortField == oldField) {
            self.page = 1;
            self.sortField = self.fields[0];
            self.search();

        // Case where the changed field is different than the sorted field.
        } else {
            self.updateRows();
        }
    };

    /**
     * Deletes the field.
     */
    self.deleteField = function(field) {
        // Prevent deletes when a delete would result in 0 fields.
        if (self.fields.length == 1) {
            return false;
        }

        // Get index of field in field array
        var index = self.fields.indexOf(field);

        // Remove field
        self.fields.splice(index, 1);

        // Update headers
        self.setHeaders();

        // Case when deleted field is the sort field - Need to change sort, page, and re search
        if (self.sortField == field) {
            self.page = 1;
            self.sortField = self.fields[0];
            self.search();

        // Case when sort field index is < delete index
        } else {
            self.updateRows();
        }
    };

    /**
     * Change the sort field.
     * If the index matches the old index, change the sort order
     * If the new index  does not match, assume asecending order
     * If the order or the index has changes, assume page 1
     */
    self.changeSort = function() {
        self.page = 1;
        self.search();
    };

    /**
     * Emit details event with object of the index'th row.
     */
    self.rowClick = function(index) {
        self.onDetails({
            record: self.records[index],
            time: self.time,
            type: self.type
        });
    };

    /**
     * Update list of available page sizes.
     * page sizes should be less than the total number of records.
     */
    self.updatePageSizes = function() {
        var newSizes = [];
        for(var i = 0; i < self.defaultSizes.length; i++) {
            if (self.defaultSizes[i] <= self.count) {
                newSizes.push(self.defaultSizes[i]);
            }
        }
        if (newSizes.length == 0) {
            newSizes.push(self.defaultSizes[0]);
        }
        self.pageSizes = newSizes;
    };

    /**
     * Call the search api and update rows and records.
     */
    self.search = function() {
        self.busy = true;
        var params = {
            model: self.type,
            time: self.time,
            filters: self.filters,
            index: (self.page - 1) * self.pageSize,
            count: self.pageSize
        };
        if (self.sortField) {
            params.orders = [{
                model: self.sortField.type,
                property: self.sortField.property,
                direction: self.sortDirection
            }];
        }

        cloudSnitchApi.searchSome(params).then(function(data) {
            self.setRecords(data.records);
            self.count = data.count;
            self.updatePageSizes();
            self.busy = false;
        }, function(resp) {
            messagingService.error(
                self.frameId,
                "API ERROR",
                resp.status + " " + resp.statusText
            );
            self.busy = false;
        });
    };

    function syncFrame() {
        self.onSyncFrame({
            data: {
                fields: self.fields,
                page: self.page,
                pageSize: self.pageSize,
                sortFieldIndex: self.fields.indexOf(self.sortField),
                sortDirection: self.sortDirection,
            }
        });
    }

    /**
     * Sync the frame with parent if this frame is visible.
     */
    self.$doCheck = function() {
        if (self.focused) {
            syncFrame();
        }
    };
}

angular.module('cloudSnitch').component('resultsFrame', {
    templateUrl: '/static/web/html/panes/results.html',
    controller: ['typesService', 'messagingService', 'cloudSnitchApi', ResultsFrameController],
    bindings: {
        fields: '<',
        filters: '<',
        focused: '<',
        page: '<',
        pageSize: '<',
        sortFieldIndex: '<',
        sortDirection: '<',
        time: '<',
        type: '<',
        onDetails: '&',
        onSyncFrame: '&'
    }
});

/**
 * Controller for looking at specific objects and immediate children.
 */
function DetailsFrameController(timeService, typesService, messagingService, cloudSnitchApi) {
    var self = this;

    /**
     * Sorted list of non identity and non created_at properties.
     */
    function objKeys() {
        var index;
        var keys = Object.keys(self.obj).sort();

        // Remove identity key
        index = keys.indexOf(typesService.identityProperty(self.type));
        if (index > -1) {
            keys.splice(index, 1);
        }

        // Remove created_at key
        index = keys.indexOf("created_at");
        if (index > -1) {
            keys.splice(index, 1);
        }
        return keys;
    }

    self.$onInit = function() {
        self.frameId = 'details_' + Date.now();
        self.timeBusy = false;
        self.objectBusy = false;

        // self.type - from bindings
        // self.time - from bindings
        self.searchTime = self.time;

        // self.record - from bindings

        // Extract identity property from record
        self.obj = self.record[self.type];
        self.identity = self.obj[typesService.identityProperty(self.type)];

        // Times the subgraph was updated
        self.times = [];

        // Sorted list of properties
        self.properties = [];

        // Object for managing children
        self.children = {};
        self.childrenKeys = []; // Used to enforce order on iteration

        // Run initial update
        self.update();
    };

    /**
     * Determine if data is still loading.
     */
    self.isBusy = function() {
        var busy = false;
        if (self.timeBusy) { return true; }
        if (self.objBusy) { return true; }
        angular.forEach(self.children, function(obj, ref) {
            if (obj.busy) { busy = true; }
        });
        return busy;
    };

    /**
     * Update list of times an object was updated.
     */
    self.updateTimes = function() {
        if (self.times.length > 0) {
            return;
        }

        self.times = [];
        self.timeBusy = true;

        cloudSnitchApi.times(
            self.type,
            self.identity,
            self.time
        ).then(function(data) {
            for (var i = 0; i < data.times.length; i++) {
                var t = data.times[i];
                t = timeService.fromMilliseconds(t);
                t = t.local(t);
                t = timeService.str(t);
                self.times.push(t);
                self.timeBusy = false;
            }
        }, function(resp) {
            messagingService.error(self.frameId,
                                   "API ERROR",
                                   resp.status + " " + resp.statusText);
            self.timeBusy = false;
        });
    };

    /**
     * Update the object
     */
    self.updateObject = function() {
        self.objectBusy = true;

        cloudSnitchApi.searchAll(
            self.type,
            self.identity,
            self.time,
            undefined,
            function(data) {
                if (data.records.length > 0) {
                    self.record = data.records[0];
                    self.obj = self.record[self.type];
                    self.properties = objKeys();
                }
            }
        ).then(function(result) {
            self.objectBusy = false;
        }, function(resp) {
            messagingService.error(self.frameId,
                                   "API ERROR",
                                   resp.status + " " + resp.statusText);
            self.objectBusy = false;
        });
    };

    /**
     * Update children.
     */
    function searchChildren(ref, label) {
        self.children[ref].records = [];
        self.children[ref].busy = true;
        cloudSnitchApi.searchAll(
            label,
            undefined,
            self.time,
            [{
                model: self.type,
                property: typesService.identityProperty(self.type),
                operator: '=',
                value: self.identity
            }],
            function(data) {
                angular.forEach(data.records, function(item) {
                    self.children[ref].records.push(item);
                    self.children[ref].rows.push(
                        childValues(self.children[ref], item)
                    );
                });
            }
        ).then(function(result) {
            self.children[ref].busy = false;
        }, function(resp) {
            messagingService.error(self.frameId,
                                   "API ERROR",
                                   resp.status + " " + resp.statusText);
            self.children[ref].busy = false;
        });
    }

    /**
     * Get array of headers for child table.
     */
    function childHeaders(label) {
        return typesService.glanceViews[label];
    }

    /**
     * Get array of values for child table
     */
    function childValues(childObj, childRecord) {
        var props = typesService.glanceViews[childObj.label];
        var obj = childRecord[childObj.label];
        var values = [];
        for (var i = 0; i < props.length; i++) {
            values.push(obj[props[i]]);
        }
        return values;
    };

    /**
     * Update children.
     */
    self.updateChildren = function() {
        var modelChildren = typesService.typeMap[self.type].children;
        self.childrenKeys = [];

        self.children = {};
        angular.forEach(modelChildren, function(value, key) {
            // Initalize obj to track loading and records
            self.childrenKeys.push(key);
            self.children[key] = {
                label: value.label,
                headers: childHeaders(value.label),
                records: [],
                rows: [],
                show: false,
                busy: false
            };
            // Perform the search
            searchChildren(key, value.label);
        });
        self.childrenKeys.sort();
    };

    /**
     * Update current object and object's children for a given time.
     */
    self.update = function() {
        self.updateChildren();
        self.updateObject();
        self.updateTimes();
    };

    /**
     * Toggle display of children.
     */
    self.toggleChild = function(childObj) {
        childObj.show = !childObj.show;
    };

    /**
     * Fires the on-details event. Adds another details frame
     */
    self.rowClick = function(obj, index) {
        self.onDetails({
            record: obj.records[index],
            time: self.searchTime,
            type: obj.label
        });
    };

    function syncFrame() {
        self.onSyncFrame({
            data: {time: self.time}
        });
    }

    /**
     * Sync the frame with parent if the frame is visible.
     */
    self.$doCheck = function() {
        if (self.focused) {
            syncFrame();
        }
    };
}

angular.module('cloudSnitch').component('detailsFrame', {
    templateUrl: '/static/web/html/panes/details.html',
    controller: ['timeService', 'typesService', 'messagingService', 'cloudSnitchApi', DetailsFrameController],
    bindings: {
        focused: '<',
        record: '<',
        time: '<',
        type: '<',
        onDetails: '&',
        onSyncFrame: '&'
    }
});


/**
 * The diff view controller covers rendering a visualization of
 *   sub graph differences.
 */
function DiffViewController($scope, $interval, $window, cloudSnitchApi, typesService, timeService, messagingService) {
    var self = this;

    var frame = undefined;
    var nodeMap = undefined;
    var nodes = undefined;
    var nodeCount = 0;

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

    self.$onInit = function() {
        self.state = 'loadingStructure';

        self.detailNode = undefined;
        self.detailNodeType = undefined;
        self.detailNodeId = undefined;

        // self.diff Comes from data binding.
        self.prevDiff = undefined;
        self.update();
    };

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
        cloudSnitchApi.diffNodes(self.diff.type, self.diff.id, self.diff.leftTime, self.diff.rightTime, offset, nodePageSize)
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
                self.state = 'done';
            }
        }, function(resp) {
            stopPollingNodes();
            self.state = 'error';
            messagingService.error("diff",
                                   "API ERROR",
                                   resp.status + " " + resp.statusText);
        });
    }

    function nodeClickHandler(d) {
        d3.event.preventDefault();
        var index = nodeMap[d.data.model][d.data.id];
        if (angular.isDefined(index) && nodes[index]) {
            $scope.$apply(function() {
                self.detailNodeType = d.data.model;
                self.detailNode = nodes[index];
                self.detailNodeId = d.data.id;
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

    self.humanState = function() {
        switch (self.state) {
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

    self.detailProps = function() {
        var props = [];
        angular.forEach(self.detailNode.left, function(value, key) {
            props.push(key);
        });
        angular.forEach(self.detailNode.right, function(value, key) {
            props.push(key);
        });
        angular.forEach(self.detailNode.both, function(value, key) {
            props.push(key);
        });
        props = props.filter(function(value, index, self) {
            return self.indexOf(value) === index;
        });
        props.sort();
        return props;
    }

    self.detailProp = function(prop, side) {
        var r = {
            val: '',
            css: ''
        }
        if (angular.isDefined(self.detailNode.both[prop])) {
            r.val = self.detailNode.both[prop];
        }
        else {
            r.val = self.detailNode[side][prop] || '';
            if (side == 'left')
                r.css = 'diffLeft';
            else
                r.css = 'diffRight';
        }
        return r;
    };

    self.closeDetail = function () {
        self.detailNode = undefined;
        self.detailNodeType = undefined;
        self.detailNodeId = undefined;
    }

    function getStructure() {
        cloudSnitchApi.diffStructure(self.diff.type, self.diff.id, self.diff.leftTime, self.diff.rightTime)
        .then(function(result) {

            if (!angular.isDefined(result.frame)) {
                return;
            }

            stopPolling();

            if (result.frame !== null) {
                self.state = 'loadingNodes';
                frame = result.frame;
                nodeMap = result.nodemap;
                nodeCount = result.nodecount;
                nodes = new Array(nodeCount);
                pollNodes = $interval(getNodes, pollInterval);
                render();
            } else {
                self.state = 'empty'
                frame = null;
                nodeMap = null;
                nodeCount = 0;
                nodes = [];
            }
        }, function(resp) {
            stopPolling();
            self.state = 'error'
            messagingService.error("diff",
                                   "API ERROR",
                                   resp.status + " " + resp.statusText);
        });
    }

    self.update = function() {
        frame = undefined;
        nodeMap = undefined;
        nodes = undefined;
        nodeCount = 0;
        self.state = 'loadingStructure';
        pollStructure = $interval(getStructure, pollInterval);
    };

    self.$onDestroy = function() {
        stopPolling();
        stopPollingNodes();
    };

    angular.element($window).bind('resize', function() {
        if (self.state != 'loadingStructure') {
            render();
            updateLabels();
        }
    });

    self.close = function() {
        self.onClose({});
    };
}

angular.module('cloudSnitch').component('diffView', {
    templateUrl: '/static/web/html/panes/diff.html',
    controller: [
        '$scope',
        '$interval',
        '$window',
        'cloudSnitchApi',
        'typesService',
        'timeService',
        'messagingService',
        DiffViewController
    ],
    bindings: {
        diff: '<',
        onClose: '&'
    }
});
