/**
 * Main controller. Holds various app wide things.
 */
angular.module("cloudSnitch").controller("ReportingController", ["$scope", "$log", "reportsService", "cloudSnitchApi", "messagingService", function($scope, $log, reportsService, cloudSnitchApi, messagingService) {
    $scope.reports = reportsService.reports;
    $scope.serverErrors = null;
    $scope.showJsonParams = false;

    $scope.data = null;

    $scope.controls = {
        reportName: "",
        report: null,
        parameters: {}
    };

    $scope.busy = false;

    $scope.$on("reports:update", function() {
        $scope.reports = reportsService.reports;
    });

    $scope.$watch("controls.reportName", function(newValue) {
        if (newValue) {
            $scope.controls.report = reportsService.get(newValue);
            $scope.controls.parameters = {};
        } else {
            $scope.controls.report = null;
        }
    });

    /**
     * Update a report control.
     */
    $scope.update = function(change) {
        $scope.controls.parameters[change.name] = change.value;
    };

    /**
     * Run the report.
     */
    $scope.submit = function() {
        var type = "web";
        $scope.busy = true;
        $scope.serverErrors = null;

        cloudSnitchApi.runReport($scope.controls.reportName, type, $scope.controls.parameters).then(function(data) {
            $scope.data = data;
            $scope.busy = false;
        }, function(resp) {
            $scope.serverErrors = resp.data;
            $scope.busy = false;
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
        return $scope.controls.reportName + "_" + new Date().toISOString() + "." + type;
    }

    /**
     * Download the data as csv or json format.
     */
    $scope.download = function(type) {

        var blobType, blobStr;

        if (type == "csv") {
            blobType = "text/csv";
            blobStr = Papa.unparse($scope.data);
        } else {
            blobType = "application/json";
            blobStr = JSON.stringify($scope.data);
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


    $scope.closeRendering = function() {
        $scope.data = null;
    };

    /**
     * Toggle display of json params use in report api request.
     */
    $scope.toggleShowJsonParams =  function() {
        $scope.showJsonParams = !$scope.showJsonParams;
    };
}]);
