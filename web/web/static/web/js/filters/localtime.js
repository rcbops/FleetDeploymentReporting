angular.module("cloudSnitch").filter("localtime", ["timeService", function(timeService) {
    return function(input) {
        return timeService.str(timeService.local(timeService.fromMilliseconds(input)));
    };
}]);
