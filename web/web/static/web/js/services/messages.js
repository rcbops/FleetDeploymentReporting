angular.module("cloudSnitch").factory("messagingService", ["$rootScope", function($rootScope) {
    var service = {};

    service.notify = function(level, target, subject, msg) {
        $rootScope.$broadcast("notify", {
            target: target,
            subject: subject,
            level: level,
            msg: msg
        });
    };

    service.error = function(target, subject, msg) {
        service.notify("ERROR", target, subject, msg);
    };

    service.warning = function(target, subject, msg) {
        service.notify("WARNING", target, subject, msg);
    };

    service.success = function(target, subject, msg) {
        service.notify("SUCCESS", target, subject, msg);
    };

    return service;
}]);
