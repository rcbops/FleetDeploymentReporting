/**
 * Controller for many input
 */
function ManyController() {
    var self = this;

    /**
     * Init values from options with defaults.
     */
    self.$onInit = function() {
        self.values     = self.values             || self.options.default || [];
        self.label      = self.options.label      || '';
        self.help_text  = self.options.help_text  || null;
        self.min_length = self.options.min_length || null;
        self.max_length = self.options.max_length || null;
        self.name       = self.options.name       || '';

        if (self.min_length > 0) {
            for (var i = 0; i < self.min_length; i++) {
                self.values.push(null);
            }
        }
        self.change();
    };

    /**
     * Can one of the items be removed?
     *
     * True for no min_length
     * True if current length exceeds min_length
     */
    self.canRemove = function() {
        if (!self.min_length) {
            return true;
        }
        return self.min_length < self.values.length;
    };

    /**
     * Remove one item at the specified index from the list.
     */
    self.remove = function(index) {
        if (self.canRemove()) {
            self.values.splice(index, 1);
        }
    }

    /**
     * Can a new item be added?
     *
     * True if no max_length
     * True if current length is less than the max_length
     */
    self.canAdd = function() {
        if (!self.max_length) {
            return true;
        }
        return self.max_length > self.values.length;
    }

    /**
     * Add a new item with a null value.
     */
    self.add = function() {
        if (self.canAdd()) {
            self.values.push(null);
        }
    }

    /**
     * Called when a child element fires a onChange
     * Updates the values and then trigger this component's onChange
     */
    self.update = function(index, change) {
        self.values[index] = change.value;
        self.change();
    };

    self.change = function() {
        self.onChange({
            change: {
                name: self.name,
                value: self.values
            }
        });
    };
}

angular.module('cloudSnitch').component('manyInput', {
    templateUrl: '/static/web/html/inputs/manyinput.html',
    controller: [ManyController],
    bindings: {
        all: '<',
        values: '<',
        options: '<',
        serverErrors: '<',
        onChange: '&',
    }
});


/**
 * Controller for time picker input.
 */
function TimeController(timeService) {
    var self = this;

    /**
     * Init controller with sane defaults.
     */
    self.$onInit = function() {
        self.valueMS   = self.valueMS           || self.options.default    || timeService.milliseconds(timeService.now());
        self.valueSTR  = timeService.str(timeService.fromMilliseconds(self.valueMS))

        self.required  = self.options.required  || true;
        self.help_text = self.options.help_text || "Please select a time.";
        self.label     = self.options.label     || "Time";
        self.name      = self.options.name      || "time";
        self.prevValue = null;
        self.change();
    };

    self.$doCheck = function() {
        if (!angular.equals(self.prevValue, self.value)) {
                self.prevValue = self.value;
                self.change();
        }
    }

    /**
     * Trigger the on change method.
     */
    self.change = function() {
        var m = timeService.fromstr(self.valueSTR);
        self.valueMS = timeService.milliseconds(m);
        self.onChange({
            change: {
                name: self.name,
                value: self.valueMS
            }
        });
    };

}

angular.module('cloudSnitch').component('timeInput', {
    templateUrl: '/static/web/html/inputs/timeinput.html',
    controller: ['timeService', TimeController],
    bindings: {
        all: '<',
        value: '<',
        options: '<',
        serverErrors: '<',
        onChange: '&'
    }
});


/**
 * Controller for a Model select dropdown.
 */
function ModelController(typesService) {
    var self = this;

    /**
     * Init the controller with sane defaults.
     */
    self.$onInit = function() {
        self.value     = self.value             || self.options.default     || 'Environment';
        self.required  = self.options.required  || true;
        self.help_text = self.options.help_text || "Please select a Model.";
        self.label     = self.options.label     || "Model";
        self.name      = self.options.name      || "model";

        self.modelChoices = [];
        for (var i = 0; i < typesService.types.length; i++) {
            self.modelChoices.push(typesService.types[i].label);
        }
        self.change();
    };

    /**
     * Trigger the on change method.
     */
    self.change = function() {
        self.onChange({
            change: {
                name: self.name,
                value: self.value
            }
        });
    };
}

angular.module('cloudSnitch').component('modelInput', {
    templateUrl: '/static/web/html/inputs/modelinput.html',
    controller: ['typesService', ModelController],
    bindings: {
        all: '<',
        value: '<',
        options: '<',
        serverErrors: '<',
        onChange: '&'
    }
});

/**
 * Controller for a generic select drop down.
 */
function SelectController() {
    var self = this;

    /**
     * Init the controller with sane defaults.
     */
    self.$onInit = function() {
        self.value     = self.value             || self.options.default;
        self.required  = self.options.required  || true;
        self.help_text = self.options.help_text || "Please select an item from the list.";
        self.label     = self.options.label     || "Select";
        self.name      = self.options.name      || "select";
        self.choices   = self.options.choices   || [];
        self.change();
    };

    /**
     * Trigger the on change method.
     */
    self.change = function() {
        self.onChange({
            change: {
                name: self.name,
                value: self.value
            }
        });
    };
}

angular.module('cloudSnitch').component('selectInput', {
    templateUrl: '/static/web/html/inputs/selectinput.html',
    controller: ['typesService', SelectController],
    bindings: {
        all: '<',
        value: '<',
        options: '<',
        serverErrors: '<',
        onChange: '&'
    }
});

/**
 * Controller for a Model dropdown with a property dropdown.
 */
function ModelPropertyController(typesService) {

    var self = this;

    /**
     * Init the controller with sane defaults
     */
    self.$onInit = function() {
        self.value = self.value || self.options.default || {model: null, prop: null};

        self.value.model    = self.value.model    || 'Environment';
        self.value.prop     = self.value.prop     || 'account_number_name';

        self.required  = self.options.required    || true;
        self.help_text = self.options.help_text   || "Please select a model and a property belonging to that model.";
        self.label     = self.options.label       || "Model and Property";
        self.name      = self.options.name        || "modelproperty";
        self.watches   = self.options.watches     || null;

        self.previousWatchedValue = null;

        self.modelChoices = [];
        self.propertyChoices = [];

        self.updateModelChoices();
        self.updatePropertyChoices();
        self.change();
    };

    /**
     * Check for a change in a watched model input.
     *
     * If changed, update model choices.
     */
    self.$doCheck = function() {
        if (self.watches) {
            if (!angular.equals(self.previousWatchedValue, self.all[self.watches])) {
                self.previousWatchedValue = angular.copy(self.all[self.watches]);
                self.updateModelChoices();
            }
        }
    };

    /**
     * Update model choices.
     *
     * If watching a model input, new choices are the path of that model
     * Otherwise use all models.
     */
    self.updateModelChoices = function() {
        var available;

        // Check for watched model
        if (self.watches) {
            available = typesService.path(self.all[self.watches])

        // Default to all models.
        } else {
            available = [];
            for (var i = 0; i < typesService.types.length; i++) {
                available.push(typesService.types[i].label);
            }
        }

        self.modelChoices = available;

        // If current model selection is not in new choices, set to null
        if (self.value && !self.modelChoices.includes(self.value.model)) {
            self.value.model = null;
        }

        // Trigger property changes also
        self.modelChange();
    };


    /**
     * Update property choices.
     *
     * New choices will be properties of current model selection.
     */
    self.updatePropertyChoices = function() {
        if (!self.value.model) {
            self.propertyChoices = [];
        } else {
            self.propertyChoices = typesService.properties[self.value.model];
        }

    };

    /**
     * Trigger property choice update and check value of current property.
     */
    self.modelChange = function() {
        self.updatePropertyChoices();
        if (!self.propertyChoices.includes(self.value.prop)) {
            self.value.prop = null;
        }
        self.change();
    };

    /**
     * Trigger this component's on change method.
     */
    self.change = function() {
        self.onChange({
            change: {
                name: self.name,
                value: self.value
            }
        });
    };
}

angular.module('cloudSnitch').component('modelPropertyInput', {
    templateUrl: '/static/web/html/inputs/modelpropertyinput.html',
    controller: ['typesService', ModelPropertyController],
    bindings: {
        all: '<',
        value: '<',
        options: '<',
        serverErrors: '<',
        onChange: '&'
    }
});
