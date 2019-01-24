/**
 * Directive for validating date time for use with the time service.
 */
angular.module("cloudSnitch").directive("dateTime", function() {
    var format = "YYYY-MM-DD HH:mm:ss";
    return {
        require: "ngModel",
        link: function(scope, elm, attrs, ctrl) {
            function timeValidator(ngModelValue) {
                var m = moment(ngModelValue, format, true);
                ctrl.$setValidity("dateTime", m.isValid());
                return ngModelValue;
            }
            ctrl.$parsers.push(timeValidator);
        }
    };
});

angular.module("cloudSnitch").directive("dateTimeForceVal", function() {
    return {
        require: "ngModel",
        link: function(scope, elm, attrs, ctrl) {
            scope.$watch(attrs["ngModel"], function (v) {
                ctrl.$setViewValue(null);
                ctrl.$setViewValue(v);
            });
        }
    };
});
