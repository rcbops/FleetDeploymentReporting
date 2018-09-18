function AlertsController($scope, $filter, $log) {
    var self = this;

    self.$onInit = function() {
        self.alerts = {
          'error': {},
          'warning': {},
          'success': {}
        };
    };

    self.removeAlert = function(level, index) {
        delete self.alerts[level][index];
        if (self.alerts.length == 0) {
            self.onNoAlerts({});
        }
    };

    $scope.$on('notify', function(notification, args) {
        if (args.target == self.target) {
            level = $filter('lowercase')(args.level);
            self.alerts[level][args.subject] = args;
            if (self.alerts.length == 1) {
                self.onHasAlerts({});
            }
        }
    });
}

angular.module('cloudSnitch').component('hxAlert', {
    templateUrl: '/static/web/html/alert.html',
    controller: ['$scope', '$filter', '$log', AlertsController],
    bindings: {
        target: '<',
        onHasAlerts: '&',
        onNoAlerts: '&'
    }
});
