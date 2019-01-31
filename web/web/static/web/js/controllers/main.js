/**
 * Main controller. Holds various app wide things.
 */
angular.module("cloudSnitch").controller("MainController", ["$scope", "$route", "typesService", function($scope, $route, typesService) {

    $scope.subApp = null;
    $scope.types = [];
    $scope.typesService = typesService;
    $scope.ready = false;

    function handleRouteChange() {
        $scope.subApp = $route.current.action || null;
    }

    $scope.$watch("typesService.isLoading()", function(isLoading) {
        if (!isLoading) {
            $scope.ready = true;
        }
    });

    $scope.$on("$routeChangeSuccess", handleRouteChange);

    // @TODO - Remove these operators. They now come from the typesService
    $scope.operators = [
        "=",
        "<",
        "<=",
        ">",
        ">=",
        "<>",
        "CONTAINS",
        "STARTS WITH",
        "ENDS WITH"
    ];

    $scope.changeSubApp = function(newApp) {
        $scope.subApp = newApp;
    };
}]);
