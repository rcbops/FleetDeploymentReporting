function BigBusyController() {}

angular.module("cloudSnitch").component("bigbusy", {
    templateUrl: "/static/web/html/bigbusy.html",
    controller: BigBusyController,
    bindings: {
        busy: "<",
        text: "<",
    }
});


/**
 * Controller for expandable table content.
 * Also includes a filter function.
 * Input is an array of arrays where the nested arrays are a single row.
 */
function ExpandableTableContentController() {

    var self = this;

    self.$onInit = function() {
        self.placeholder = self.placeholder || "Filter";
        self.prevLength = undefined;

        // Maintain a string representation of each actual row. Filtering will
        // search the shadow row instead of the actual row.
        self.shadowRows = [];

        self.rows = self.rows || [];
        self.count = self.rows.length;

        self.filter = self.filter || "";
        self.filtered = [];
        self.expanded = self.expanded || false;
    };

    /**
     * Runs each digest. Determine if we need to update the shadow rows.
     */
    self.$doCheck = function() {
        if (self.rows.length != self.prevLength) {
            self.shadowRows = [];
            for (var i = 0; i < self.rows.length; i++) {
                self.shadowRows.push(self.rows[i].join().toLowerCase());
            }
            self.prevLength = self.rows.length;
        }
    };

    /**
     * Determine if the row at index is included by the filter
     */
    self.isIncluded = function(index) {
        if (index < 0 || index >= self.rows.length) {
            return false;
        }
        return (!self.filter || self.shadowRows[index].indexOf(self.filter.toLowerCase()) > -1);
    };

    /**
     * Toggle the show/hide of the table
     */
    self.toggleExpand = function() {
        self.expanded = !self.expanded;
    };

    /**
     * Register row click events
     */
    self.rowClick = function(index) {
        self.onRowClick({index: index});
    };
}

angular.module("cloudSnitch").component("expandableTableContent", {
    templateUrl: "/static/web/html/expandabletablecontent.html",
    controller: ExpandableTableContentController,
    bindings: {
        headers: "<",
        rows: "<",
        expanded: "<",
        title: "<",
        placeholder: "<",
        filter: "<",
        onRowClick: "&"
    }
});

function CSFieldController(typesService) {
    var self = this;

    self.$onInit = function() {
        self.displayType = typesService.displayType(self.label, self.property) || "text";
    };
}

angular.module("cloudSnitch").component("csField", {
    templateUrl: "/static/web/html/csfield.html",
    controller: ["typesService", CSFieldController],
    bindings: {
        label: "<",
        property: "<",
        value: "<"
    }
});

