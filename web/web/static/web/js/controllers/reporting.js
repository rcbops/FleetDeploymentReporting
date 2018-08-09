/**
 * Main controller. Holds various app wide things.
 */
angular.module('cloudSnitch').controller('ReportingController', ['$scope', 'reportsService', 'cloudSnitchApi', function($scope, reportsService, cloudSnitchApi) {
    $scope.reports = reportsService.reports;
    $scope.serverErrors = null;
    $scope.rendered = false;
    $scope.showJsonParams = false;
    $scope.controls = {
        reportName: '',
        report: null,
        parameters: {}
    };

    $scope.busy = false;

    $scope.$on('reports:update', function(event) {
        $scope.reports = reportsService.reports;
    });

    $scope.$watch('controls.reportName', function(newValue) {
        if (newValue) {
            $scope.controls.report = reportsService.get(newValue);
            $scope.controls.parameters = {};
        } else {
            $scope.controls.report = null;
        }
    });

    $scope.update = function(change) {
        $scope.controls.parameters[change.name] = change.value;
    };

    function suggestedFileName(type) {
        var d = new Date();
        var name =
            $scope.controls.reportName + '_' +
            d.toISOString() + '.' +
            type;
        return name;
    }

    function renderData(data) {
        $scope.rendered = false;
        var thead = $('#renderTable thead');
        var tbody = $('#renderTable tbody');

        // Empty the table
        thead.html("");
        tbody.html("");
        if (data.length < 1) {
            var empty = $('<tr><td>No Matching Results</td></tr>');
            tbody.append(empty);
            return;
        }

        headers = Object.keys(data[0])
        var tr = $('<tr></tr>');
        angular.forEach(headers, function(header) {
            var th = $('<th></th>').text(header);
            tr.append(th);
        });
        thead.append(tr);

        angular.forEach(data, function(row) {
            var tr = $('<tr></tr>');
            angular.forEach(headers, function(header) {
                var td = $('<td></td>').text(row[header]);
                tr.append(td);
            });
            tbody.append(tr);
        });
        $scope.rendered = true;
    }

    function handleData(type, data) {
        if (type == 'json' || type == 'csv') {
            // Create link to blob
            var url = window.URL.createObjectURL(data);
            var link = angular.element('<a>Download</a>');
            link.css('display', 'none');
            link.attr('href', url);
            link.attr('download', suggestedFileName(type));

            // Add to document and simulate click
            angular.element(document.body).append(link);
            link[0].click();

            // Clean up
            link.remove();
            URL.revokeObjectURL(url);

        // Build simple web view
        } else {
            renderData(data);
        }
        $scope.busy = false;
    }

    $scope.submit = function(type) {
        $scope.busy = true;
        $scope.serverErrors = null;

        cloudSnitchApi.runReport($scope.controls.reportName, type, $scope.controls.parameters).then(function(data) {
            handleData(type, data);
        }, function(resp) {
            $scope.serverErrors = resp.data;
            $scope.busy = false;
        });
    };

    $scope.closeRendering = function() {
        $('#renderTable thead').html("");
        $('#renderTable tbody').html("");
        $scope.rendered = false;
    };

    $scope.toggleShowJsonParams =  function() {
        $scope.showJsonParams = !$scope.showJsonParams;
    };
}]);
