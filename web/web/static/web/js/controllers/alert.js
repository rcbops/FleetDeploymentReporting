angular.module('cloudSnitch').controller('AlertController', ['$scope', '$attrs', '$filter', '$log', function($scope, $attrs, $filter, $log) {
    /*
   {  
      function: "updateTimes",
      message: resp.statusText
      status: resp.status,
      subject: "times",
      type: "ERROR",
    });
    **/
    $scope.alerts = {};
    
    $scope.$on('notification:api', function(event, args){
      if ( args.subject == $attrs.mySubject && $filter('lowercase')(args.type) == $attrs.type) {
        args.notification = 'API ' + args.type;
        $scope.alerts[args.subject] = args;
      }
    });

    $scope.removeAlert = function(index) {
        delete $scope.alerts[index];
    };
}]);
