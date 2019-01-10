"use strict";

/**
 * Controller for pie chart component.
 * Data should be passed as an array of
 * {
 *    label: 'somestring',
 *    value: 123
 * }
 * objects with value indicating the number of times
 * label has occurred.
 */
function PieChartController($element, $timeout) {

    var self = this;

    const arcGen = d3.pie()
        .sort(null)
        .value(d => d.value);

    const sizing = {
        sm: {
            donutWidth: 42,
            title: {
                x: 10,
                y: 20,
            }
        }
        // @TODO - Add additional sizing
    };

    /**
     * Limit data to maxSlices by grouping every slice that would exceed
     * the maximum into one slice for 'Other'
     */
    function prepareData() {
        var prepared;
        // Group extra slices together if capped
        if (!self.showAll && self.data.length > self.maxSlices) {
            prepared = self.data.slice(0, self.maxSlices - 1);
            var s = 0;
            for (var i = self.maxSlices - 1; i < self.data.length; i++) {
                s += self.data[i].value;
            }
            prepared.push({
                label: 'Other',
                value: s
            });
        } else {
            prepared = self.data.slice(0);
        }
        return prepared;
    }

    /**
     * Gather dimensions of the svg element.
     */
    function dimensions() {
        return {
            width: parseInt(self.svg.style('width')),
            height: parseInt(self.svg.style('height'))
        }
    }

    /**
     * Update center
     */
    function updateCenter() {
        const d = dimensions();
        self.svg.select('g.all').attr("transform", `translate(${d.width / 2}, ${d.height / 2})`);
    }

    /**
     * Update the pie chart and redraw.
     */
    function update() {
        self.preparedData = prepareData();

        // Determine inner and outer radius.
        const d = dimensions();
        var radius = Math.min(d.width, d.height) / 2 - 20;
        var arc = d3.arc()
            .innerRadius(radius - sizing[self.size].donutWidth)
            .outerRadius(radius);

        // Make sure we have a minimum color range
        const colorDomain = self.preparedData.map(d => d.label);
        var i = 0;
        while (colorDomain.length < self.minColors) {
            colorDomain.push("_" + i + "_");
            i++;
        }

        const arcs = arcGen(self.preparedData);
        const color = d3.scaleOrdinal()
            .domain(colorDomain)
            .range(d3.quantize(t => d3.interpolateCool(t), colorDomain.length).reverse());

        updateCenter();

        var g = self.svg.select('g.all');
        // Remove old paths
        g.selectAll('path').remove();
        // Add new paths
        g.selectAll('path')
            .data(arcs)
            .enter().append('path')
                .attr('fill', d => color(d.data.label))
                .attr('stroke', '#fff')
                .attr('d', arc)
            .append('title')
                .text(d => d.data.label);
    }

    self.toggleCtrls   = function() { self.ctrlsVisible = !self.ctrlsVisible; };
    self.toggleShowAll = function() { update(); }
    self.changeSlices  = function() { update(); }

    self.$onInit = function() {
        console.log("Inside chart update");
        // Return early if empty data
        if (self.data.length < 1) { return; }

        self.ctrlsVisible = false;
        self.minColors = 3;
        self.maxSlicesMin = 1;
        self.maxSlicesMax = self.data.length;
        self.maxSlices = Math.min(20, self.maxSlicesMax);

        self.showAll = false;
        if (self.data.length == self.maxSlices) {
            self.showAll = true;
        }

        // Only sm is supported right now
        self.size = self.size || 'sm';

        // Wait till page renders
        $timeout(function() {
            console.log("inside timeout");
            self.svg = d3.select($element[0]).select('svg');

            var svgTitle = self.svg.select('g.title').append('text')
                .attr('font', '16px sans-serif')
                .attr('x', sizing[self.size].title.x)
                .attr('y', sizing[self.size].title.y)
                .attr('stroke', '#444')
                .text(self.title);

            self.svg.append("g")
                .attr('class', 'all');
            update();
        });

        window.addEventListener('resize', update);
    };

    /**
     * Remove window event listeners created during $onInit
     */
    self.$onDestroy = function() { window.removeEventListener('resize', update); };
}

angular.module('cloudSnitch').component('piechart', {
    templateUrl: '/static/web/html/charts/pie.html',
    controller: ['$element', '$timeout', PieChartController],
    bindings: {
        data: '<',
        size: '<',
        title: '<'
    }
});
