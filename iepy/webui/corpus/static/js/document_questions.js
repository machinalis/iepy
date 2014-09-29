"use strict";

$(document).ready(function () {
    var $segments = $(".segments");
    var $svg = $("svg");
    $svg.attr("width", $segments.width());
    $svg.attr("height", $segments.height());

    $(".toolbox label input").each(function(){
        var $this = $(this);
        $this.parent().addClass("toolbox-option-{0}".format($this.val()));
    });

});


function QuestionsController($scope) {

    // ### Attributes ###

    $scope.eo_selected = undefined; // Id of the selected occurrence

    // Publish into the scope the variables defined globally
    $scope.eos = window.eos;
    $scope.relations = window.relations;
    $scope.forms = window.forms;
    $scope.current_tool = window.initial_tool;
    $scope.arrows = {};

    $(document).ready(function(){
        $scope.svg = $("svg")[0];

        $scope.update_relations_arrows();
        $(window).resize($scope.update_relations_arrows);
    });

    // ### Methods ###


    $scope.update_relations_arrows = function () {

        for (var form_id in $scope.forms) {
            var path = $scope.arrows[form_id];
            if (path) {
                $scope.svg.removeChild(path);
            }
        }

        for (var i in $scope.relations) {
            var rel_obj = $scope.relations[i];
            $scope.calculate_arrow_string(
                rel_obj.relation[0],
                rel_obj.relation[1],
                rel_obj.form_id
            );
        }
    });

    // ### Methods ###

    // Sets the value for selectable on all entity occurrences
    $scope.set_selectables = function (value) {
        for (var i in $scope.eos) {
            $scope.eos[i].selectable = value;
        }
    };

    $scope.eo_click = function (id) {
        var eo = $scope.eos[id];

        // Not selectable
        if (!eo.selectable) { return; }

        if ($scope.eo_selected === undefined) {
            // Marking as selected
            eo.selected = eo.selected + 1;
            $scope.eo_first_click(id);
        } else {
            $scope.eo_second_click(id);
        }
    };


    $scope.eo_first_click = function (id) {
        $scope.eo_selected = id;

        $scope.set_selectables(false);
        $scope.eos[id].selectable = true;
        // Calculate wich ones must be selectable
        for (var i in $scope.relations) {
            var rel = $scope.relations[i];
            var rel_index = rel.relation.indexOf(id);
            if (rel_index >= 0) {
                var eo_id = $scope.relations[i].relation[(rel_index + 1) % 2];
                $scope.eos[eo_id].selectable = true;
            }
        }
    };

    $scope.eo_second_click = function (id) {
        if ($scope.eo_selected === id) {
            // You're de-selecting the one you've just selected
            $scope.eos[id].selected = $scope.eos[id].selected - 1;
        } else {
            $scope.eos[id].selected = $scope.eos[id].selected + 1;
            var eo_id1 = $scope.eo_selected;
            var eo_id2 = id;

            for (var i in $scope.relations) {
                var rel = $scope.relations[i];
                var eo_rel_index1 = rel.relation.indexOf(eo_id1);
                var eo_rel_index2 = rel.relation.indexOf(eo_id2);
                if (eo_rel_index1 >= 0 && eo_rel_index2 >= 0) {
                    var form_value = $scope.forms[rel.form_id];
                    var new_value = form_value ? "": $scope.current_tool;
                    $scope.forms[rel.form_id] = new_value;

                    $scope.calculate_arrow_string(
                        rel.relation[0],
                        rel.relation[1],
                        rel.form_id
                    );

                    if (!new_value) {
                        $scope.eos[eo_id1].selected = $scope.eos[eo_id1].selected - 2;
                        $scope.eos[eo_id2].selected = $scope.eos[eo_id2].selected - 2;
                    }

                }
            }
        }

        $scope.set_selectables(true);
        $scope.eo_selected = undefined;
    };

    $scope.calculate_arrow_string = function (eo_id1, eo_id2, form_id) {
        if (!$scope.forms[form_id]) {
            // Remove the arrow
            path = $scope.arrows[form_id];
            $scope.svg.removeChild(path);
        } else {
            // Curve configuration
            var curve_distance = 20;
            var y_offset = $($scope.svg).position().top;
            var x_offset = 60;

            // Entity occurrences
            var $eo1 = $(".eo-" + eo_id1);
            var $eo2 = $(".eo-" + eo_id2);

            // Positions
            var eo1_pos = $eo1.position();
            var eo2_pos = $eo2.position();

            // Corrected positions
            var eo1_pos_left = eo1_pos.left - x_offset;
            var eo1_pos_top = eo1_pos.top - y_offset - 5;
            var eo2_pos_left = eo2_pos.left - x_offset;
            var eo2_pos_top = eo2_pos.top - y_offset - 10;

            // Form value
            var form_value = $scope.forms[form_id];

            // Format should be:
            // M<x1>,<y1> C<x1>,<y1 + distance> <x2>,<y2 + distance> <x2>,<y2>
            var curve_string = "M{0},{1} C{0},{4} {2},{5} {2},{3}".format(
                Math.round(eo1_pos_left), // {0}
                Math.round(eo1_pos_top),  // {1}
                Math.round(eo2_pos_left), // {2}
                Math.round(eo2_pos_top),  // {3}
                Math.round(eo1_pos_top - curve_distance), // {4}
                Math.round(eo2_pos_top - curve_distance)  // {5}
            );

            var path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
            path.innerHTML = 'createElementNS';
            path.setAttribute("class", 'arrow arrow_{0}'.format(form_value));
            path.setAttribute("style", 'marker-end: url(#arrow-point-{0});'.format(
                form_value
            ));
            path.setAttribute("d", curve_string);

            $scope.svg.appendChild(path);
            $scope.arrows[form_id] = path;
        }
    };
}

String.prototype.format = String.prototype.f = function() {
    var s = this;
    var i = arguments.length;

    while (i--) {
        s = s.replace(new RegExp('\\{' + i + '\\}', 'gm'), arguments[i]);
    }
    return s;
};
