$(document).ready(function () {
    "use strict";

    $(document).foundation();

    $(".toolbox label input").each(function () {
        var $this = $(this);
        $this.parent().addClass("toolbox-option-{0}".format($this.val()));
    });

});

var app = window.angular.module('labelingApp', ['ngResource', 'ngRoute', 'ngCookies']).run(
    function ($http, $cookies) {
        $http.defaults.headers.post['X-CSRFToken'] = $cookies.csrftoken;
        // Add the following two lines
        $http.defaults.xsrfCookieName = 'csrftoken';
        $http.defaults.xsrfHeaderName = 'X-CSRFToken';
    });

app.factory('EntityOccurrence', ['$resource',
        function ($resource) {
            return $resource('/corpus/crud/entity_occurrence/', {'pk': '@pk'}, {});
        }]
    );
app.factory('TextSegment', ['$resource',
        function ($resource) {
            return $resource('/corpus/crud/text_segment/', {'pk': '@pk'}, {});
        }]
    );
app.directive('ngRightClick', function ($parse) {
    return function ($scope, element, attrs) {
        var fn = $parse(attrs.ngRightClick);
        element.bind('contextmenu', function (event) {
            $scope.$apply(function () {
                event.preventDefault();
                fn($scope, {$event: event});
            });
        });
    };
});
app.controller('QuestionsController', ['$scope', 'EntityOccurrence', 'TextSegment',
function ($scope, EntityOccurrence, TextSegment) {
    "use strict";
    // ### Attributes ###

    $scope.eo_selected = undefined; // Id of the selected occurrence

    // Publish into the scope the variables defined globally
    $scope.eos = window.eos;
    $scope.relations = window.relations;
    $scope.forms = window.forms;
    $scope.current_tool = window.initial_tool;
    $scope.arrows = {};
    $scope.eo_modal = {};

    $(document).ready(function () {
        $scope.$segments = $(".segments");
        $scope.$svg = $("svg");
        $scope.svg = $scope.$svg[0];

        $(window).resize($scope.update_relations_arrows);

        $scope.update_relations_arrows();
        $scope.create_relations_metadata();

        $(".eo-submenu").on("click", $scope.on_eo_submenu_click);
        $(".eo-submenu").mouseover($scope.highlight_eo_tokens);
        $(".eo-submenu").mouseout($scope.highlight_eo_tokens);
        $(".entity-occurrence").mouseover($scope.highlight_eo_tokens);
        $(".entity-occurrence").mouseout($scope.highlight_eo_tokens);
        $(".prev-relations li").mouseover($scope.highlight_relation);
        $(".prev-relations li").mouseout($scope.highlight_relation);
        $scope.eo_modal.elem = $('#eoModal');
        $scope.eo_modal.elem.find('a.cancel').bind('click', function () {
            $scope.eo_modal.elem.foundation('reveal', 'close');
        });
        $scope.eo_modal.elem.find('a.save').bind('click', function () {
            $scope.eo_modal.submit();
        });
    });

    // ### Methods ###

    $scope.create_relations_metadata = function () {
        // NOTE: update_relations_arrows must be run before

        var $holder = $(".prev-relations");
        var $holder_wrapper = $(".prev-relations-wrapper");

        for(var i in $scope.relations) {
            if ($scope.relations.hasOwnProperty(i)) {
                var relation = $scope.relations[i];
                var info = relation.info;
                var form_value = $scope.forms[relation.form_id];

                if (form_value !== null && info !== undefined) {
                    var $element = $("<li>");
                    var $arrow = $("<i>");
                    var $text = $("<span>");

                    $arrow.addClass("fi-arrow-right");
                    $arrow.addClass("prev-arrow prev-arrow-{0}".format(form_value));
                    $text.text(info);

                    $element.addClass("prev-relation-{0}".format(relation.form_id));
                    $element.data("relation-id", relation.form_id);
                    $element.append($arrow);
                    $element.append($text);
                    $holder.append($element);

                    $holder_wrapper.fadeIn();
                }
            }
        }
    };

    $scope.update_relations_arrows = function () {
        // Update width and height of the svg element
        $scope.$svg.attr("width", $scope.$segments.width());
        $scope.$svg.attr("height", $scope.$segments.height());

        // Remove all arrows before re-drawing
        for (var form_id in $scope.forms) {
            if ($scope.forms.hasOwnProperty(form_id)) {
                var path = $scope.arrows[form_id];
                if (path) {
                    $scope.svg.removeChild(path);
                }
            }
        }

        // Re-draw all the arrows
        for (var i in $scope.relations) {
            if ($scope.relations.hasOwnProperty(i)) {
                var rel_obj = $scope.relations[i];
                $scope.calculate_arrow_string(
                    rel_obj.relation[0],
                    rel_obj.relation[1],
                    rel_obj.form_id
                );
            }
        }
    };

    // Sets the value for selectable on all entity occurrences
    $scope.set_selectables = function (value) {
        for (var i in $scope.eos) {
            if ($scope.eos.hasOwnProperty(i)) {
                $scope.eos[i].selectable = value;
            }
        }
    };

    $scope.eo_click = function (ids) {
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

        if ($scope.eo_selected === undefined) {
            // Marking as selected
            $scope.eo_first_click(id);
        } else {
            $scope.eo_second_click(id);
        }
    };

    $scope.highlight_eo_tokens = function () {
        var $this = $(this);
        var eo_id = $this.data("eo-id");
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
                    if (eo_rel_index1 >= 0 && eo_rel_index2 >= 0) {
                        var form_value = $scope.forms[rel.form_id];
                        var new_value = form_value ? "": $scope.current_tool;
                        $scope.forms[rel.form_id] = new_value;

                        $scope.calculate_arrow_string(
                            rel.relation[0],
                            rel.relation[1],
                            rel.form_id
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

    $scope.calculate_arrow_string = function (eo_id1, eo_id2, form_id) {
        var path;

        if ($scope.forms[form_id] === null || $scope.forms[form_id] === "") {
            // Remove the arrow
            path = $scope.arrows[form_id];
            var $prev_arrow = $(".prev-relation-{0}".format(form_id));
            if ($prev_arrow.length > 0) {
                $prev_arrow.remove();
            }
            if (path !== undefined) {
                $scope.svg.removeChild(path);
            }
        } else {
            // Curve configuration
            var curve_distance = 25;
            var y_offset = $($scope.svg).position().top;
            var x_offset = -30;

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

            path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
            path.setAttribute("class", 'arrow arrow_{0}'.format(form_value));
            path.setAttribute("style", 'marker-end: url(#arrow-point-{0});'.format(
                form_value
            ));
            path.setAttribute("d", curve_string);

            $scope.svg.appendChild(path);
            $scope.arrows[form_id] = path;
        }
    };

    // ###  Entity Occurrence Modification methods (and modal)  ###

    $scope.manage_eo = function (value, segment_id) {
        EntityOccurrence.get({pk: value}).$promise.then(
            function (eo_obj) {
                var $modal = $scope.eo_modal.elem;
                var marker_html = '<div class="marker"><span class="rotate">';
                marker_html +=    '<i class="fi-arrows-expand"></span></div>';
                $modal.find('.message').empty();
                $modal.find('.segment').empty();
                TextSegment.get({pk: segment_id}).$promise.then(
                    function (segment) {
                        // store resources on the scope
                        $scope.eo_modal.eo = eo_obj;
                        $scope.eo_modal.segment = segment;
                        var $segment = $modal.find('.segment');
                        for (var i = 0; i < segment.tokens.length; i++) {
                            if (segment.offset + i === eo_obj.offset) {
                                $segment.append(marker_html);
                            }
                            if (segment.offset + i === eo_obj.offset_end) {
                                $segment.append(marker_html);
                            }
                            $segment.append(
                                '<div class="token">' + segment.tokens[i] + '</div>'
                            );
                        }
                        $scope.eo_modal.update_selection();
                        $segment.sortable({
                            cancel: ".token",
                            update: $scope.eo_modal.update_selection
                        });
                    },
                    function (response) {
                        $scope.eo_modal.add_msg("Server error " + response);
                    }
                );
                $modal.foundation('reveal', 'open');
            });
    };

    $scope.eo_modal.reset = function () {
        var $elem = $scope.eo_modal.elem;
        $elem.find('.message').empty();
        $elem.find('.segment').empty();
    };

    $scope.eo_modal.add_msg = function (msg) {
        $scope.eo_modal.elem.find('.message').empty().append('<p>' + msg + '</p>');
    };

    $scope.eo_modal.update_selection = function (event) {
        var paiting = false;
        var new_offsets = [];
        $scope.eo_modal.elem.find('.segment div').each(function (idx) {
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
        var base = $scope.eo_modal.segment.offset;
        $scope.eo_modal.eo.new_offset = base + new_offsets[0];
        $scope.eo_modal.eo.new_offset_end = base + new_offsets[1] - 1;
    };

    $scope.eo_modal.submit = function () {
        var eo = $scope.eo_modal.eo;
        if (eo.new_offset_end - eo.new_offset <= 0) {
            $scope.eo_modal.add_msg("Invalid Entity Occurrence limits. Can't be empty.");
        } else {
            eo.offset = eo.new_offset;
            eo.offset_end = eo.new_offset_end;
            eo.$save().then(
                $scope.eo_modal.save_success,
                function (response) {
                    $scope.eo_modal.add_msg("Not saved. " + response.statusText);
                }
            );
        }
    };

    $scope.eo_modal.save_success = function () {
        /* Here is handled not the segment on the modal, but on the actual underlying
         * page */
        $('#partial-save').val('enabled').parents('form').submit();
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
