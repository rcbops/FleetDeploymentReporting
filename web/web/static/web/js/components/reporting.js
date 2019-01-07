function ReportRenderController() {
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
        headers = Object.keys(self.data[0])
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

angular.module('cloudSnitch').component('reportrender', {
    templateUrl: '/static/web/html/reports/render.html',
    controller: [ReportRenderController],
    bindings: {
        data: '<'
    }
});
