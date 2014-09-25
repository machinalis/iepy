"use strict";

function QuestionsController($scope) {

    // ### Attributes ###

    $scope.eo_selected = undefined; // Id of the selected occurrence

    // Publish into the scope the variables defined globally
    $scope.eos = window.eos;
    $scope.relations = window.relations;
    $scope.forms = window.forms;

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
                    var new_value = form_value ? false : true;
                    $scope.forms[rel.form_id] = new_value;
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
}
