angular.module('cloudSnitch').factory('reportsService', ['$rootScope', '$log', 'cloudSnitchApi', function($rootScope, $log, cloudSnitchApi) {

    var service = {};

    service.reports = [];
    service.reportsMap = {};
    service.reportsLoading = true;

    /**
     * Update reports from api
     */
    service.updateReports = function() {
        service.reports = [];
        service.reportsMap = {}
        service.reportsLoading = true;

        cloudSnitchApi.reports().then(function(result) {
            service.reports = result;
            service.reportsLoading = false;
            for (var i = 0; i < service.reports.length; i++) {
                service.reportsMap[service.reports[i].name] = service.reports[i];
            }
            $rootScope.$broadcast('reports:update');
        }, function(error) {
            // @TODO - Do something with error
            $log.log("In promise failure updateReports");
            $rootScope.$broadcast("notification:api",
                              {
                                 function: "updateReports",
                                 message: resp.statusText,
                                 status: resp.status,
                                 subject: "reports",
                                 type: "ERROR"
                              });
            service.reports = [];
        });
    }

    /**
     * Get a specific report from local reports.
     */
    service.get = function(name) {
        var report = service.reportsMap[name];
        if (!angular.isDefined(report)) {
            report = null;
        }
        return report;
    };

    /**
     * Update the service.
     */
    service.update = function() {
        service.updateReports();
    };

    /**
     * Is the service still loading?
     */
    service.isLoading = function() {
        return service.reportsLoading;
    };

    service.update()
    return service;
}]);
