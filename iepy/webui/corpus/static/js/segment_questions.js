var occurrences_by_id = {};

$(document).ready(function () {
    "use strict";

    $(".question .entity-occurrence")
        .mouseover(on_question_occurrence_hover)
        .mouseout(on_question_occurrence_hover);

    generate_occurrences_by_id();
});

function generate_occurrences_by_id() {
    "use strict";

    $(".segment .entity-occurrence").each(function () {
        var $this = $(this);
        var ids = $this.data("occurrence-ids");
        for (var i in ids) {
            if (ids[i] in occurrences_by_id) {
                occurrences_by_id[ids[i]].push($this);
            } else {
                occurrences_by_id[ids[i]] = [$this];
            }
        }
    });
}

function on_question_occurrence_hover() {
    var $this = $(this);
    var occurrence_id = $this.data("occurrence-id");
    for (var i in occurrences_by_id[occurrence_id]) {
        var $occurrence = occurrences_by_id[occurrence_id][i];
        $occurrence.toggleClass("hover");
    }
}
