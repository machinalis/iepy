"use strict"

function QuestionsController($scope){

    // ### Attributes ###

    $scope.eo_selected = undefined; // Id of the selected occurrence

    // Publish into the scope the variables defined globally
    $scope.eos = eos;
    $scope.relations = relations;
    $scope.forms = forms;

    // ### Methods ###

    // Sets the value for selectable on all entity occurrences
    $scope.set_selectables = function(value){
        for(var i in eos){
            eos[i].selectable = value;
        }
    }

    $scope.eo_click = function(id){
        var eo = eos[id];

        // Not selectable
        if(!eo.selectable){ return; }

        if($scope.eo_selected === undefined){
            // Marking as selected
            eo.selected = eo.selected + 1;
            $scope.eo_first_click(id);
        } else {
            $scope.eo_second_click(id);
        }
    }


    $scope.eo_first_click = function(id){
        $scope.eo_selected = id;

        $scope.set_selectables(false);
        eos[id].selectable = true;
        // Calculate wich ones must be selectable
        for(var i in relations){
            var rel = relations[i];
            var rel_index = rel.relation.indexOf(id);
            if(rel_index >= 0){
                var eo_id = relations[i].relation[(rel_index + 1) % 2];
                eos[eo_id].selectable = true;
            }
        }
    }

    $scope.eo_second_click = function(id){
        if($scope.eo_selected == id){
            // You're de-selecting the one you've just selected
            eos[id].selected = eos[id].selected - 1;
        } else{
            eos[id].selected = eos[id].selected + 1;
            var eo_id1 = $scope.eo_selected;
            var eo_id2 = id;

            for(var i in relations){
                var rel = relations[i];
                var eo_rel_index1 = rel.relation.indexOf(eo_id1);
                var eo_rel_index2 = rel.relation.indexOf(eo_id2);
                if(eo_rel_index1 >= 0 && eo_rel_index2 >= 0){
                    var form = forms[i];
                    var value = form.value ? false : true;
                    form.value = value;
                    if(!value){
                        eos[eo_id1].selected = eos[eo_id1].selected - 2;
                        eos[eo_id2].selected = eos[eo_id2].selected - 2;
                    }

                }
            }
        }

        $scope.set_selectables(true);
        $scope.eo_selected = undefined;
    }
}
