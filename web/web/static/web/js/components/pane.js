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

angular.module("cloudSnitch").component("panetopctrl", {
    templateUrl: "/static/web/html/panes/panetopctrl.html",
    controller: [PaneTopCtrlController],
    bindings: {
        backable: "<",
        cloneable: "<",
        diffable: "<",
        onClose: "&",
        onClone: "&",
        onDiff: "&",
        onBack: "&"
    }
});

/**
 * Controller for the panes component.
 *  Handles multiple panes and directs pane to pane communication.
 */
function PanesController($route, $location, timeService, typesService, paramService) {
    var self = this;

    const queryParams = {
        diff: "diff",
        panes: "panes"
    };

    // Handle initial state from $location. Check routeParams and query params.
    function handleLocation() {
        var i;

        // Check for :type and :id params from current route
        if (angular.isDefined($route.current.pathParams.type) && angular.isDefined($route.current.pathParams.id)) {
            self.panes.push({
                topFrame: {
                    state: "details",
                    type: $route.current.pathParams.type,
                    identity: $route.current.pathParams.id,
                    time: timeService.str(timeService.now())
                }
            });
        }

        // Scrub location
        $location.path("/browse");

        // Check query string for diff
        self.diff = paramService.search(queryParams.diff) || undefined;

        // Check query string for panes.
        self.panes = self.panes.concat(paramService.search(queryParams.panes) || []);

        // Limit panes to first maxPanes
        self.panes = self.panes.slice(0, self.maxPanes);

        // Build frames from top frames for each pane
        for (i = 0; i < self.panes.length; i++) {
            self.panes[i].frames = [self.panes[i].topFrame];
        }
    }

    // Sync url query string with current state
    function syncLocation() {
        paramService.search(queryParams.diff, self.diff || null);
        paramService.search(queryParams.panes, self.panes || []);
    }

    self.$onInit = function() {
        self.maxPanes = self.maxPanes || 2;
        self.panes = [];
        self.diff = undefined;

        handleLocation();

        // Start with one pane if none provided from params.
        if (self.panes.length < 1) { self.add();}
    };

    self.$onDestroy = function() {
        // Scrub query params
        angular.forEach(queryParams, function(v) {
            paramService.search(v, null);
        });
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
        syncLocation();
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
     * @TODO - disallow same times.
     */
    self.diffable = function() {
        if (self.panes.length > 1) {
            var a = self.panes[0].topFrame;
            var b = self.panes[1].topFrame;

            if (a === undefined || b === undefined) {
                return false;
            }

            // Both panes must be on details to be diffable
            if (a.state != "details" || b.state != "details") {
                return false;
            }

            // Both panes must be on the same type
            if (a.type != b.type) {
                return false;
            }

            // Both panes must have the same identity
            if (a.identity != b.identity) {
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
            id: a.identity,
            leftTime: a.time,
            rightTime: b.time
        };
        syncLocation();
    };

    /**
     * Handle a diff close.
     */
    self.closeDiff = function() {
        self.diff = undefined;
        syncLocation();
    };
}

angular.module("cloudSnitch").component("panes", {
    templateUrl: "/static/web/html/panes/panes.html",
    controller: ["$route", "$location", "timeService", "typesService", "paramService", PanesController],
    bindings: {
        maxPanes: "<",
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
        });
    }

    self.$onInit = function() {
        self.cloneable = self.cloneable || false;
        self.diffable = self.diffable || false;
        self.frames = self.frames || [];
        self.id = timeService.str(timeService.now());

        // Add initial frame if None
        if (self.frames.length == 0) {
            self.frames.push({state: "search"});
        }
        paneChange();
    };

    /**
     * Get the identity value of a frame.
     */
    self.identity = function(index) {
        return self.frames[index].identity;
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
            state: "results",
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
    self.details = function(identity, time, type) {
        self.frames.push({
            state: "details",
            identity: identity,
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

angular.module("cloudSnitch").component("pane", {
    templateUrl: "/static/web/html/panes/pane.html",
    controller: ["typesService", "timeService", PaneController],
    bindings: {
        cloneable: "<",
        diffable: "<",
        index: "<",
        frames: "<",
        onClone: "&",
        onClose: "&",
        onDiff: "&",
        onPaneChange: "&"
    }
});

/**
 * Controller for the frame that presents search controls.
 */
function SearchFrameController(typesService, timeService) {
    var self = this;

    self.typesService = typesService;

    self.$onInit = function() {
        self.path = undefined;
        self.type = self.type || "Environment";
        self.filters = self.filters || [];

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
            operator: "=",
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

angular.module("cloudSnitch").component("searchFrame", {
    templateUrl: "/static/web/html/panes/search.html",
    controller: ["typesService", "timeService", SearchFrameController],
    bindings: {
        filters: "<",
        focused: "<",
        time: "<",
        type: "<",
        onSearch: "&",
        onSyncFrame: "&"
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
        self.frameId = "results_" + Date.now();
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
        self.sortDirection =  self.sortDirection || "asc";

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
        self.records = records;
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
        var i;
        var field;
        var fieldSet = new Set([]);
        for(i = 0; i < self.fields.length; i++) {
            fieldSet.add(fieldToStr(self.fields[i]));
        }

        // Loop over reversed path types and stop at first field not in set.
        for (i = 0; i < self.path.length && !field; i++) {
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
            var lastProps = typesService.properties[lastType];
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
        var idProp = typesService.identityProperty(self.type);
        self.onDetails({
            identity: self.records[index][self.type][idProp],
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

angular.module("cloudSnitch").component("resultsFrame", {
    templateUrl: "/static/web/html/panes/results.html",
    controller: ["typesService", "messagingService", "cloudSnitchApi", ResultsFrameController],
    bindings: {
        fields: "<",
        filters: "<",
        focused: "<",
        page: "<",
        pageSize: "<",
        sortFieldIndex: "<",
        sortDirection: "<",
        time: "<",
        type: "<",
        onDetails: "&",
        onSyncFrame: "&"
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
        self.frameId = "details_" + Date.now();
        self.timeBusy = false;
        self.objectBusy = false;

        // self.type - from bindings
        // self.time - from bindings
        self.searchTime = self.time;

        // Update object later from id
        self.obj = {};

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
        angular.forEach(self.children, function(obj) {
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
            messagingService.error(
                self.frameId,
                "API ERROR",
                resp.status + " " + resp.statusText
            );
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
        ).then(function() {
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
                operator: "=",
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
        ).then(function() {
            self.children[ref].busy = false;
        }, function(resp) {
            messagingService.error(
                self.frameId,
                "API ERROR",
                resp.status + " " + resp.statusText
            );
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
    }

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
        var idProp = typesService.identityProperty(obj.label);
        self.onDetails({
            identity: obj.records[index][obj.label][idProp],
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

angular.module("cloudSnitch").component("detailsFrame", {
    templateUrl: "/static/web/html/panes/details.html",
    controller: ["timeService", "typesService", "messagingService", "cloudSnitchApi", DetailsFrameController],
    bindings: {
        focused: "<",
        identity: "<",
        time: "<",
        type: "<",
        onDetails: "&",
        onSyncFrame: "&"
    }
});


/**
 * The diff view controller covers rendering a visualization of
 *   sub graph differences.
 */
function DiffViewController($scope, $interval, $window, cloudSnitchApi, typesService, timeService, messagingService) {
    var self = this;

    var frame = undefined;
    var pollStructure;
    var pollInterval = 3000;

    var maxLabelLength = 0;
    var viewerHeight = null;
    var viewerWidth = null;
    var duration = 750;
    var root;

    var margin = {
        top: 20,
        bottom: 20,
        right: 250,
        left: 250
    };

    var tree = undefined;
    var nodeRadius = 10;

    var svg = undefined;
    var g = undefined;

    self.$onInit = function() {
        self.state = "loadingStructure";
        // self.diff Comes from data binding.
        self.prevDiff = undefined;
        self.update();
    };

    function zoom() {
        g.attr("transform", d3.event.transform);
    }
    var zoomListener = d3.zoom().scaleExtent([0.1, 3]).on("zoom", zoom);

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
        return model + ": " + id;
    }

    /**
     * Compute size of svg and the tree.
     */
    function sizeTree() {
        var p = svg.select(function() {
            return this.parentNode;
        });
        svg.attr("width", 1);
        svg.attr("height", 1);

        var pNode = p.node();
        var rect = pNode.getBoundingClientRect();
        var style = window.getComputedStyle(pNode);
        var paddingLeft = parseInt(style.getPropertyValue("padding-left"));
        var paddingRight = parseInt(style.getPropertyValue("padding-right"));
        var paddingTop = parseInt(style.getPropertyValue("padding-top"));
        var paddingBottom = parseInt(style.getPropertyValue("padding-bottom"));

        var svgHeight = rect.height - paddingTop - paddingBottom;
        var svgWidth = rect.width - paddingLeft - paddingRight;
        svg.attr("height", svgHeight);
        svg.attr("width", svgWidth);

        var sizeX = svgWidth - margin.right - margin.left;
        var sizeY = svgHeight - margin.bottom - margin.top;
        return {x: sizeX, y: sizeY};
    }

    /**
     * Offset the tree containing "g" element by margin.
     */
    function translateTree() {
        g.attr("transform", "translate(" + margin.left + "," + margin.top + ")");
    }

    /**
     * Center view port on a node
     */
    function centerNode(source) {
        var t = d3.zoomTransform(svg.node());
        var x = -source.y0;
        var y = -source.x0;
        x = x * t.k + viewerWidth / 2;
        y = y * t.k + viewerHeight / 2;
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
        var path = `M ${s.y} ${s.x}
                    C ${(s.y + d.y) / 2} ${s.x},
                      ${(s.y + d.y) / 2} ${d.x},
                      ${d.y} ${d.x}`;

        return path;
    }

    function render() {
        // Get the svg element
        if (!angular.isDefined(svg)) {
            svg = d3.select("svg#diff");
        }
        svg.call(zoomListener);

        // Make a svg g element if not defined.
        if (!angular.isDefined(g)) {
            g = svg.append("g");
        }
        g.html("");

        var s = sizeTree();
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
        if (angular.isDefined(root.children)) {
            root.children.forEach(function(child){
                collapse(child);
            });
        }

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
            maxLabelLength = Math.max(label(d).length, maxLabelLength);
        });

        childCount(0, root);
        var newHeight = d3.max(levelWidth) * 25; // 25 pixels per line
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
                var classes = "node";
                if (d.children)
                    classes += " node--internal";
                else
                    classes += " node--leaf";

                switch(d.data.flags.length) {
                case 1:
                    if (d.data.flags[0] == "t1") {
                        classes += " removed";
                    } else if (d.data.flags[0] == "t2") {
                        classes += " added";
                    }
                    break;
                case 2:
                    classes += " both";
                    break;
                default:
                    classes += " unchanged";

                }
                return classes;
            })
            .attr("transform", function() {
                return "translate(" + source.y0 + "," + source.x0 + ")";
            })
            .on("click", click)
            .on("contextmenu", nodeClickHandler);

        nodeEnter.append("circle")
            .attr("r", nodeRadius);

        nodeEnter.append("text")
            .attr("dy", 3)
            .attr("x", function(d) { return d.children ? -15: 15;})
            .style("text-anchor", function(d) { return d.children ? "end": "start"; })
            .style("fill-opacity", 0)
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
            .attr("transform", function() {
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
            .insert("path", "g")
            .attr("class", "link")
            .attr("d", function() {
                var o = {x: source.x0, y: source.y0 };
                return diagonal(o, o);
            });

        var linkUpdate = linkEnter.merge(link);
        linkUpdate.transition()
            .duration(duration)
            .attr("d", function(d) {
                return diagonal(d, d.parent);
            });

        link.exit().transition()
            .duration(duration)
            .attr("d", function() {
                var o = {x: source.x, y: source.y};
                return diagonal(o, o);
            })
            .remove();

        nodes.forEach(function(d) {
            d.x0 = d.x;
            d.y0 = d.y;
        });
    }

    /**
     * Handles a node click and spawns a diffdetails component.
     */
    function nodeClickHandler(d) {
        d3.event.preventDefault();
        $scope.$apply(function() {
            self.details = {
                type: d.data.model,
                identity: d.data.id
            };
        });
    }

    /**
     * Stop controller from polling for structure.
     */
    function stopPolling() {
        if (angular.isDefined(pollStructure)) {
            $interval.cancel(pollStructure);
            pollStructure = undefined;
        }
    }

    /**
     * Compute human friendly state.
     */
    self.humanState = function() {
        switch (self.state) {
        case "empty":
            return "No meaningful differences.";
        case "error":
            return "Error loading diff";
        case "loadingStructure":
            return "Loading Structure";
        case "done":
            return "Done";
        default:
            return "Unknown";
        }
    };

    /**
     * Close details component and unset self.details.
     */
    self.closeDetails = function () {
        self.details = undefined;
    };

    /**
     * Grab the structure of the diff.
     */
    function getStructure() {
        cloudSnitchApi.diffStructure(self.diff.type, self.diff.id, self.diff.leftTime, self.diff.rightTime)
            .then(function(result) {

                if (!angular.isDefined(result.frame)) {
                    return;
                }

                stopPolling();

                if (Object.keys(result.frame).length !== 0 && result.frame.constructor === Object) {
                    frame = result.frame;
                    render();
                    self.state = "done";
                } else {
                    self.state = "empty";
                    frame = null;
                }
            }, function(resp) {
                stopPolling();
                self.state = "error";
                messagingService.error(
                    "diff",
                    "API ERROR",
                    resp.status + " " + resp.statusText
                );
            });
    }

    /**
     * Update the diff.
     */
    self.update = function() {
        frame = undefined;
        self.state = "loadingStructure";
        pollStructure = $interval(getStructure, pollInterval);
    };

    /**
     * Stop polling if still going when diff is closed.
     */
    self.$onDestroy = function() {
        stopPolling();
    };

    /**
     * Rerender the graph if window size changes.
     */
    angular.element($window).bind("resize", function() {
        if (self.state != "loadingStructure") {
            render();
        }
    });

    /**
     * Close the diff component.
     */
    self.close = function() {
        self.onClose({});
    };
}

angular.module("cloudSnitch").component("diffView", {
    templateUrl: "/static/web/html/panes/diff.html",
    controller: [
        "$scope",
        "$interval",
        "$window",
        "cloudSnitchApi",
        "typesService",
        "timeService",
        "messagingService",
        DiffViewController
    ],
    bindings: {
        diff: "<",
        onClose: "&"
    }
});

function DiffDetailsController(cloudSnitchApi, messagingService) {
    var self = this;

    /**
     * Init the diff detail component.
     */
    self.$onInit = function() {
        self.prevType = undefined;
        self.prevIdentity = undefined;
        self.properties = [];
    };

    /**
     * Determine if we need to update.
     *
     * The user can click on different nodes without closing this component.
     */
    self.$doCheck = function() {
        if (self.prevType != self.type || self.prevIdentity != self.identity) {
            self.update();
            self.prevType = self.type;
            self.prevIdentity = self.identity;
        }
    };

    /**
     * Determine if the property at index is different between t1 and t2.
     *
     * This is used to determine if properties should be highlighted for
     * their differences.
     */
    self.isDifferent = function(index) {
        return self.properties[index].t1 != self.properties[index].t2;
    };

    /**
     * Update the properties.
     */
    self.update = function() {
        self.properties = [];
        self.busy = true;
        cloudSnitchApi.diffNodes(self.type, self.identity, self.leftTime, self.rightTime)
            .then(function(result) {
                self.properties = result.properties;
                self.busy = false;
            }, function(resp) {
                self.busy = false;
                messagingService.error(
                    "diffdetails",
                    "API ERROR",
                    resp.status + " " + resp.statusText
                );
            });
    };

    /**
     * Register a close event.
     */
    self.close = function() {
        self.onClose({});
    };
}

angular.module("cloudSnitch").component("diffDetails", {
    templateUrl: "/static/web/html/panes/diffdetails.html",
    controller: ["cloudSnitchApi", "messagingService", DiffDetailsController],
    bindings: {
        type: "<",
        identity: "<",
        leftTime: "<",
        rightTime: "<",
        onClose: "&"
    }
});
