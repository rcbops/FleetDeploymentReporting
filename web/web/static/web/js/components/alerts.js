function AlertsController($scope) {
    var self = this;

    self.$onInit = function() {
        self.alerts = [];
    };

    self.removeAlert = function(index) {
        self.alerts.splice(index, 1);
        if (self.alerts.length == 0) {
            self.onNoAlerts({});
        }
    };

    $scope.$on("notify", function(notification, args) {
        if (args.target == self.target) {
            self.alerts.push(args);
            if (self.alerts.length == 1) {
                self.onHasAlerts({});
            }
        }
    });
}

angular.module("cloudSnitch").component("hxAlert", {
    templateUrl: "/static/web/html/alert.html",
    controller: ["$scope", AlertsController],
    bindings: {
        target: "<",
        onHasAlerts: "&",
        onNoAlerts: "&"
    }
});
