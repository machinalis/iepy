var eo_creation_url;

$(document).ready(function () {
    "use strict";

    $(document).foundation();

    $(".toolbox label input").each(function () {
        var $this = $(this);
        $this.parent().addClass("toolbox-option-{0}".format($this.val()));
    });

});

var app = window.angular.module(
    'labelingApp',
    ['ngResource', 'ngRoute', 'ngCookies']
).run(
    function ($http, $cookies) {
        $http.defaults.headers.post['X-CSRFToken'] = $cookies.csrftoken;
        // Add the following two lines
        $http.defaults.xsrfCookieName = 'csrftoken';
        $http.defaults.xsrfHeaderName = 'X-CSRFToken';
    }
);

app.factory('EntityOccurrence', ['$resource',
    function ($resource) {
        return $resource('/corpus/crud/entity_occurrence/', {'pk': '@pk'}, {});
    }
]);
app.factory('Entity', ['$resource',
    function ($resource) {
        return $resource('/corpus/crud/entity/', {'pk': '@pk'}, {});
    }
]);

app.directive('ngRightClick', function ($parse) {
    return function ($scope, element, attrs) {
        var fn = $parse(attrs.ngRightClick);
        element.bind('contextmenu', function (event) {
            event.preventDefault();
            fn($scope, {$event: event});
        });
    };
});

app.controller('QuestionsController', ['$scope', 'EntityOccurrence', 'Entity',
function ($scope, EntityOccurrence, Entity) {
    "use strict";
    // ### Attributes ###

    $scope.eo_selected = undefined; // Id of the selected occurrence

    // Publish into the scope the variables defined globally
    $scope.eos = window.eos;
    $scope.forms = window.forms;
    $scope.relations = window.relations;
    $scope.current_tool = window.initial_tool;
    $scope.different_kind = window.different_kind;
    $scope.question_options = window.question_options;
    $scope.other_judges_labels = window.other_judges_labels;
    $scope.arrows = {};
    $scope.eo_edition_modal = {};
    $scope.eo_creation_modal = {};
    $scope.metadata_visible = "pos";
    $scope.interaction_activated = true;

    $(document).ready(function () {
        $scope.$segments = $(".segments");
        $scope.$svg = $("svg");
        $scope.svg = $scope.$svg[0];

        $(window).resize($scope.update_relations_arrows);
        $("body").keypress(function (event) {
            var $toolbox_options = $(".toolbox li input");
            var index = event.which - 49;
            if (index >= 0 && index <= 5) {
                $scope.current_tool = $scope.question_options[index];
                $($toolbox_options[index]).prop("checked", "checked");
            }
        });

        setTimeout($scope.update_relations_arrows, 300);

        $(".rich-token").on("click", function (event, stop) {
            stop = stop === undefined ? true : stop;

            if (stop) {
                event.preventDefault();
                event.stopPropagation();
            }
        });
        $(".eo-submenu").on("click", $scope.on_eo_submenu_click);
        $(".eo-submenu").mouseover($scope.highlight_eo_tokens);
        $(".eo-submenu").mouseout($scope.highlight_eo_tokens);

        $(".judge-answers-wrapper").change(function(){
            var $this = $(this);
            var selected = $this.val();
            if(selected === "me"){
                $scope.interaction_activated = true;
                $scope.update_relations_arrows();
            } else {
                $scope.interaction_activated = false;
                $scope.draw_judge_answers(selected);
            }
        });

        $(".entity-occurrence").mouseover(function () {
            var $eo = $(this);
            $scope.on_eo_mouseover($eo, false);
        });
        $(".entity-occurrence").mouseout(function () {
            var $eo = $(this);
            $scope.on_eo_mouseover($eo, true);
        });

        // EO Creation modal
        $scope.eo_creation_modal.elem = $('#eo-creation-modal');
        $scope.eo_creation_modal.elem.find('a.save').bind('click', function () {
            $scope.eo_creation_modal.submit();
        });
        $scope.eo_creation_modal.elem.find('a.cancel').bind('click', function () {
            $scope.eo_creation_modal.elem.foundation('reveal', 'close');
        });

        // EO Edition modal
        $scope.eo_edition_modal.elem = $('#eo-edition-modal');
        $scope.eo_edition_modal.elem.find('a.cancel').bind('click', function () {
            $scope.eo_edition_modal.elem.foundation('reveal', 'close');
        });
        $scope.eo_edition_modal.elem.find('a.save').bind('click', function () {
            $scope.eo_edition_modal.submit();
        });
        $scope.eo_edition_modal.elem.find('a.remove-eo-ask').bind(
            'click', $scope.eo_edition_modal.remove_eo_ask
        );
        $scope.eo_edition_modal.elem.find('a.remove-eo-confirm').bind(
            'click', $scope.eo_edition_modal.remove_eo_confirm
        );
        $scope.eo_edition_modal.elem.find('a.remove-eo-confirm-all').bind(
            'click', $scope.eo_edition_modal.remove_eo_confirm_all
        );
        $scope.eo_edition_modal.elem.find('a.remove-eo-cancel').bind(
            'click', $scope.eo_edition_modal.remove_eo_cancel
        );
    });

    // ### Methods ###

    $scope.clean_all_arrows = function () {
        // Remove all arrows before re-drawing
        $($scope.svg).find("path").each(function () {
            var $elem = $(this);
            if ($elem.parent("marker").length === 0) {
                $scope.svg.removeChild($elem[0]);
            }
        });

        $scope.arrows = {};
    };

    $scope.update_relations_arrows = function () {
        // Update width and height of the svg element
        $scope.$svg.attr("width", $scope.$segments.width());
        $scope.$svg.attr("height", $scope.$segments.height() + 100);

        $scope.clean_all_arrows();

        var data = [];
        for (var i in $scope.relations) {
            if ($scope.relations.hasOwnProperty(i)) {
                var rel_obj = $scope.relations[i];
                var path = $scope.calculate_arrow_string(
                    rel_obj.relation[0],
                    rel_obj.relation[1],
                    $scope.forms[rel_obj.form_id]
                );
                $scope.arrows[rel_obj.form_id] = path;
            }
        }
    };

    $scope.set_selectables = function (value) {
        // Sets the value for selectable on all entity occurrences
        for (var i in $scope.eos) {
            if ($scope.eos.hasOwnProperty(i)) {
                $scope.eos[i].selectable = value;
            }
        }
    };

    $scope.eo_click = function (ids) {
        // Handles only left click
        if(event.button !== 0) { return; }

        // Handles only the case of 1 id, if it has
        // more than one, it shows the menu
        if (ids.length === 1) {
            var id = ids[0];
            $scope.handle_click_on_eo(id);
        }
    };

    $scope.on_eo_submenu_click = function (event) {
        event.preventDefault();

        var $this = $(this);
        var eo_id = $this.data("eo-id");
        $scope.handle_click_on_eo(eo_id);
        $scope.$apply();
    };

    $scope.handle_click_on_eo = function (id) {
        var eo = $scope.eos[id];

        // Not selectable
        if (!eo || !eo.selectable) { return; }

        // If interaction disabled, do nothing
        if (!$scope.interaction_activated) {
            var $wrapper = $(".judge-answers-wrapper");
            $wrapper.addClass("shake shake-constant shake-rotate");
            setTimeout(function(){ $wrapper.removeClass("shake"); }, 800);
            return;
        }

        if ($scope.eo_selected === undefined) {
            // Marking as selected
            $scope.eo_first_click(id);
        } else {
            $scope.eo_second_click(id);
        }
    };

    $scope.on_eo_mouseover = function ($eo, mouseout) {
        // If interaction disabled, do nothing
        if (!$scope.interaction_activated) { return; }

        var eo_id = $eo.data("eo-id");
        mouseout = mouseout || false;

        for (var i in $scope.relations) {
            if ($scope.relations.hasOwnProperty(i)) {
                var rel_obj = $scope.relations[i];
                if (rel_obj.relation.indexOf(eo_id) === -1) {
                    var arrow = $scope.arrows[rel_obj.form_id];
                    if (mouseout) {
                        arrow.style.opacity = "";
                    } else {
                        arrow.style.opacity = ".15";
                    }
                }
            }
        }


        $(".eo-{0}".format(eo_id)).each(function () {
            var $this = $(this);
            $this.toggleClass("highlight");
        });
    };

    $scope.highlight_relation = function () {
        var $this = $(this);
        var toggle = $this.data("toggle");
        var rel_id = $this.data("relation-id");
        var arrow = $scope.arrows[rel_id];

        if (toggle) {
            $this.data("toggle", false);
            arrow.style.strokeWidth = "";
        } else {
            $this.data("toggle", true);
            arrow.style.strokeWidth = "4px";
        }

    };

    $scope.eo_first_click = function (id) {
        var eo = $scope.eos[id];
        $scope.eo_selected = id;

        $scope.set_selectables(false);
        eo.selectable = true;
        eo.selected = true;

        // Calculate wich ones must be selectable
        for (var i in $scope.relations) {
            if ($scope.relations.hasOwnProperty(i)) {
                var rel = $scope.relations[i];
                var rel_index = rel.relation.indexOf(id);
                if (rel_index >= 0) {
                    var eo_id = $scope.relations[i].relation[(rel_index + 1) % 2];
                    $scope.eos[eo_id].selectable = true;
                }
            }
        }
    };

    $scope.eo_second_click = function (id) {
        if ($scope.eo_selected === id) {
            // You're de-selecting the one you've just selected
            $scope.eos[id].selected = false;
        } else {
            var eo_id1 = $scope.eo_selected;
            var eo_id2 = id;

            for (var i in $scope.relations) {
                if ($scope.relations.hasOwnProperty(i)) {
                    var rel = $scope.relations[i];
                    var eo_rel_index1 = rel.relation.indexOf(eo_id1);
                    var eo_rel_index2 = rel.relation.indexOf(eo_id2);
                    var order_check = $scope.different_kind || eo_rel_index1 < eo_rel_index2;
                    if (eo_rel_index1 >= 0 && eo_rel_index2 >= 0 && order_check) {
                        var form_value = $scope.forms[rel.form_id];
                        var new_value = form_value ? "": $scope.current_tool;
                        $scope.forms[rel.form_id] = new_value;

                        $scope.add_or_remove_arrow(
                            rel.relation[0], rel.relation[1],
                            new_value, rel.form_id
                        );
                        $scope.eos[eo_id1].selected = false;
                        $scope.eos[eo_id2].selected = false;
                    }
                }
            }
        }

        $scope.set_selectables(true);
        $scope.eo_selected = undefined;
    };

    $scope.add_or_remove_arrow = function (eo_id1, eo_id2, value, form_id) {
        var path;

        if (value === null || value === "") {
            path = $scope.arrows[form_id];
            var $prev_arrow = $(".prev-relation-{0}".format(form_id));
            if ($prev_arrow.length > 0) {
                $prev_arrow.remove();
            }
            if (path !== undefined) {
                $scope.svg.removeChild(path);
            }
        } else {
            path = $scope.calculate_arrow_string(eo_id1, eo_id2, value);
            $scope.arrows[form_id] = path;
        }
    };

    $scope.calculate_arrow_string = function (eo_id1, eo_id2, value, alternative) {
        alternative = alternative || false;
        var path;

        // Curve configuration
        var curve_distance = 25;
        var y_offset = 10;

        if (alternative) {
            curve_distance *= 1.5;
        }

        // Entity occurrences
        var $eo1 = $(".eo-" + eo_id1);
        var $eo2 = $(".eo-" + eo_id2);

        // Positions
        var eo1_pos_top = $eo1.offset().top - $scope.$svg.offset().top;
        var eo1_pos_left = $eo1.offset().left - $scope.$svg.offset().left;
        var eo2_pos_top = $eo2.offset().top - $scope.$svg.offset().top;
        var eo2_pos_left = $eo2.offset().left - $scope.$svg.offset().left;

        // Corrected positions
        var eo1_pos_shifted_left = eo1_pos_left + $eo1.width() / 4;
        var eo1_pos_shifted_top = eo1_pos_top - y_offset;
        var eo2_pos_shifted_left = eo2_pos_left + $eo2.width() / 4;
        var eo2_pos_shifted_top = eo2_pos_top - y_offset;

        // Format should be:
        // M<x1>,<y1> C<x1>,<y1 + distance> <x2>,<y2 + distance> <x2>,<y2>
        var curve_string = "M{0},{1} C{0},{4} {2},{5} {2},{3}".format(
            Math.round(eo1_pos_shifted_left), // {0}
            Math.round(eo1_pos_shifted_top),  // {1}
            Math.round(eo2_pos_shifted_left), // {2}
            Math.round(eo2_pos_shifted_top),  // {3}
            Math.round(eo1_pos_shifted_top - curve_distance), // {4}
            Math.round(eo2_pos_shifted_top - curve_distance)  // {5}
        );

        path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
        path.setAttribute("class", 'arrow arrow_{0}'.format(value));
        path.setAttribute("style", 'marker-end: url(#arrow-point-{0});'.format(
            value
        ));
        path.setAttribute("d", curve_string);
        $scope.svg.appendChild(path);

        return path;
    };

    // ###  Entity Occurrence Modification methods (and modal)  ###

    $scope.token_context_menu = function (token_id) {
        var $dropdown = $("#token-edition-dropdown");
        var $token = $(".rich-token-" + token_id);
        var $modify_eo_item = $dropdown.find("#modify-eo-item");
        var $create_eo_item = $dropdown.find("#create-eo-item");
        $create_eo_item.unbind("click");
        $create_eo_item.on("click", function (event) {
            event.preventDefault();
            $scope.display_creation_modal($token);
            $scope.eo_creation_modal.selected = $token;
        });

        if ($token.hasClass("entity-occurrence")) {
            var segment_id = $token.parents(".segment").data("segment-id");
            var entity_id = $token.data("eo-id");
            $modify_eo_item.unbind("click");
            $modify_eo_item.on("click", function (event) {
                event.preventDefault();
                $scope.display_edition_modal(entity_id, segment_id);
            });
            $modify_eo_item.show();
        } else {
            $modify_eo_item.hide();
        }

        $token.trigger("click", false);
    };

    $scope.display_edition_modal = function (value, segment_id) {
        EntityOccurrence.get({pk: value}).$promise.then(
            function (eo_obj) {
                var $modal = $scope.eo_edition_modal.elem;
                var marker_html = '<div class="marker"><span class="rotate">';
                marker_html +=    '<i class="fi-arrows-expand"></span></div>';
                $modal.find('.message').empty();
                $modal.find('.segment').empty();
                $modal.find('.entity_id span').text(eo_obj.entity);
                $modal.find('.entity_kind span').text(eo_obj.entity__kind__name);

                $scope.eo_edition_modal.eo = eo_obj;

                var $eo = $(".eo-" + eo_obj.pk);
                var $tokens = $eo.parent(".segment").find(".rich-token");
                var $segment = $modal.find('.segment');
                $tokens.each(function(){
                    var $this = $(this);
                    var $token = $("<div>");
                    $token.addClass("token");
                    $token.text($this.find(".token").text());
                    $token.data("offset", $this.find(".token").data("offset"));
                    if($this.hasClass("eo-" + eo_obj.pk)){
                        $token.addClass("eo");
                    }
                    $segment.append($token);
                });

                var eo_tokens = $segment.find(".eo");
                $(marker_html).insertBefore($(eo_tokens[0]));
                $(marker_html).insertAfter($(eo_tokens[eo_tokens.length - 1]));
                $scope.update_selection($modal);
                $segment.sortable({
                    cancel: ".token",
                    update: function () { $scope.update_selection($modal); }
                });
                $modal.foundation('reveal', 'open');
            });
    };

    $scope.display_creation_modal = function ($selected, segment_id) {
        var $modal = $scope.eo_creation_modal.elem;
        var marker_html = '<div class="marker"><span class="rotate">';
        marker_html +=    '<i class="fi-arrows-expand"></span></div>';
        $modal.find('.message').empty();
        $modal.find('.segment').empty();

        var $tokens = $selected.parent(".segment").find(".rich-token");
        var $segment = $modal.find('.segment');
        var $new_selected = {};
        $tokens.each(function(){
            var $this = $(this);
            var $token = $("<div>");
            $token.addClass("token");
            $token.text($this.find(".token").text());
            $token.data("offset", $this.find(".token").data("offset"));
            $segment.append($token);

            if ($this.hasClass($selected.attr("class"))) {
                $new_selected = $token;
            }
        });

        $(marker_html).insertBefore($new_selected);
        $(marker_html).insertAfter($new_selected);
        $scope.update_selection($modal);
        $segment.sortable({
            cancel: ".token",
            update: function () { $scope.update_selection($modal); }
        });
        $modal.foundation('reveal', 'open');
    };

    $scope.eo_edition_modal.reset = function () {
        var $elem = $scope.eo_edition_modal.elem;
        $elem.find('.message').empty();
        $elem.find('.segment').empty();
    };

    $scope.modal_add_msg = function ($modal, msg) {
        $modal.find('.message').empty().append('<p>' + msg + '</p>');
    };

    $scope.update_selection = function ($modal) {
        var paiting = false;
        var new_offsets = [];
        $modal.find('.segment div').each(function (idx) {
            var className = 'between-markers';
            var $elem = $(this);
            $elem.removeClass(className);
            var is_marker = $elem.hasClass('marker');
            if (is_marker) {
                new_offsets.push(idx);
            }
            if (paiting && is_marker) {
                // stop paiting
                paiting = false;
            } else if (!paiting && is_marker) {
                // start paiting
                paiting = true;
            }
            // now, paint
            if (paiting && !is_marker) {
                $elem.addClass(className);
            }
        });

        if (new_offsets.length === 2) {
            var $divs = $modal.find('.segment div');
            var $first_word_in = $divs.eq([new_offsets[0] + 1]);
            var $first_word_out = $divs.eq([new_offsets[1] + 1]);
            var new_offset_end, new_offset;

            if ($first_word_out.length === 0) {
                $first_word_out = $divs.eq([new_offsets[1] - 1]);
                new_offset_end = $first_word_out.data("offset") + 1;
            } else {
                new_offset_end = $first_word_out.data("offset");
            }
            new_offset = $first_word_in.data("offset");
            if ($first_word_in.hasClass("marker")) {
                new_offset = new_offset_end;
            }

            $modal.data("new_offset", new_offset);
            $modal.data("new_offset_end",  new_offset_end);
        }
    };

    $scope.eo_edition_modal.submit = function () {
        var $modal = $scope.eo_edition_modal.elem;
        var eo = $scope.eo_edition_modal.eo;
        var new_offset = $modal.data("new_offset");
        var new_offset_end = $modal.data("new_offset_end");
        if (new_offset_end - new_offset <= 0) {
            $scope.modal_add_msg(
                $modal, "Invalid Entity Occurrence limits. Can't be empty."
            );
        } else {
            eo.offset = new_offset;
            eo.offset_end = new_offset_end;
            eo.$save().then(
                $scope.modal_save_success,
                function (response) {
                    $scope.modal_add_msg($modal, "Not saved. " + response.statusText);
                }
            );
        }
    };

    $scope.eo_creation_modal.submit = function () {
        var $modal = $scope.eo_creation_modal.elem;
        var new_offset = $modal.data("new_offset");
        var new_offset_end = $modal.data("new_offset_end");
        var $new_entity_kind = $("#new_entity_kind");
        var $document = $(".document");
        var $button = $modal.find(".save");

        if (new_offset_end - new_offset <= 0) {
            $scope.modal_add_msg(
                $modal, "Invalid Entity Occurrence limits. Can't be empty."
            );
        } else if ($new_entity_kind.val() === null) {
            $scope.modal_add_msg($modal, "Error: you must select a kind");
        } else {
            var csrftoken = getCookie('csrftoken');
            $button.find(".text").fadeOut(function () {
                $button.find(".loading").fadeIn();
            });

            $.ajax({
                url: eo_creation_url,
                type: "POST",
                data: {
                    offset: new_offset,
                    offset_end: new_offset_end,
                    kind: $new_entity_kind.val(),
                    doc_id: $document.data("document-id")
                },
                success: function () {
                    $button.find(".loading").fadeOut(function () {
                        $button.find(".text").fadeIn();
                    });
                    $scope.modal_save_success();
                },
                error: function (jqXHR, textStatus) {
                    $scope.modal_add_msg($modal, "Not saved. " + textStatus);
                },
                beforeSend: function(xhr, settings) {
                    xhr.setRequestHeader("X-CSRFToken", csrftoken);
                }
            });

        }
    };

    $scope.run_partial_save = function () {
        var $partial_save = $("#partial-save");
        if($partial_save.length !== 0){
            $partial_save.val('enabled').parents('form').submit();
        } else {
            location.reload();
        }
    };

    $scope.modal_save_success = function () {
        /* Here is handled not the segment on the modal, but on the actual underlying
         * page */
        $scope.run_partial_save();
    };
    $scope.eo_edition_modal.remove_eo_ask = function (event) {
        event.preventDefault();

        $(".remove-eo-ask").fadeOut("fast", function () {
            $(".remove-confirm-wrapper").fadeIn("fast");
        });
    };

    $scope.eo_edition_modal.remove_eo_cancel = function (event) {
        $(".remove-confirm-wrapper").fadeOut("fast", function () {
            $(".remove-eo-ask").fadeIn("fast");
        });
    };

    $scope.eo_edition_modal.remove_eo_confirm = function (event) {
        event.preventDefault();

        var eo = $scope.eo_edition_modal.eo;
        EntityOccurrence.delete({pk: eo.pk}).$promise.then(function () {
            $scope.run_partial_save();
        });
    };
    $scope.eo_edition_modal.remove_eo_confirm_all = function (event) {
        event.preventDefault();

        var eo = $scope.eo_edition_modal.eo;
        Entity.delete({pk: eo.entity}).$promise.then(function () {
            $scope.run_partial_save();
        });
    };

    $scope.draw_judge_answers = function (judge) {
        event.preventDefault();
        var data = $scope.other_judges_labels[judge];
        $scope.clean_all_arrows();
        for (var i in data) {
            if (data.hasOwnProperty(i)) {
                var path = $scope.calculate_arrow_string(
                    data[i][0], data[i][1], data[i][2], true
                );
            }
        }
    };

}
]);

String.prototype.format = String.prototype.f = function () {
    var s = this;
    var i = arguments.length;

    while (i--) {
        s = s.replace(new RegExp('\\{' + i + '\\}', 'gm'), arguments[i]);
    }
    return s;
};

// using jQuery
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
