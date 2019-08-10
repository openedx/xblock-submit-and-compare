/* Javascript for submitcompareXBlock. */
/* eslint-disable no-unused-vars */
/* eslint-disable require-jsdoc */
/**
 * Initialize the student view
 * @param {Object} runtime - The XBlock JS Runtime
 * @param {Object} element - The containing DOM element for this instance of the XBlock
 * @returns {undefined} nothing
 */
function SubmitAndCompareXBlockInitView(runtime, element) {
    'use strict';
    /* eslint-disable camelcase */
    /* eslint-enable no-unused-vars */

    var $ = window.jQuery;
    var handlerUrl = runtime.handlerUrl(element, 'student_submit');
    var hintUrl = runtime.handlerUrl(element, 'send_hints');
    var publishUrl = runtime.handlerUrl(element, 'publish_event');
    var $element = $(element);
    var $xblocksContainer = $('#seq_content');
    var submit_button = $element.find('.submit_button');
    var hint_button = $element.find('hint_button');
    var reset_button = $element.find('.reset_button');
    var problem_progress = $element.find('.problem_progress');
    var used_attempts_feedback = $element.find('.used_attempts_feedback');
    var button_holder = $element.find('.button_holder');
    var answer_textarea = $element.find('.answer');
    var your_answer = $element.find('.your_answer');
    var expert_answer = $element.find('.expert_answer');
    var hint_div = $element.find('.hint');
    var hint_button_holder = $element.find('.hint_button_holder');
    var submit_button_label = $element.find('.submit_button').attr('value');
    var hint;
    var hints;
    var hint_counter = 0;
    var xblock_id = $element.attr('data-usage-id');
    var cached_answer_id = xblock_id + '_cached_answer';
    var problem_progress_id = xblock_id + '_problem_progress';
    var used_attempts_feedback_id = xblock_id + '_used_attempts_feedback';
    if (typeof $xblocksContainer.data(cached_answer_id) !== 'undefined') {
        answer_textarea.text($xblocksContainer.data(cached_answer_id));
        problem_progress.text($xblocksContainer.data(problem_progress_id));
        used_attempts_feedback.text($xblocksContainer.data(used_attempts_feedback_id));
    }

    /**
     * Parse and display hints
     * @param {Object} result - The result payload
     * @returns {undefined} nothing
     */
    function set_hints(result) {
        hints = result.hints;
        if (hints.length > 0) {
            hint_button.css('display', 'inline');
            hint_button_holder.css('display', 'inline');
        }
    }

    $.ajax({
        type: 'POST',
        url: hintUrl,
        data: JSON.stringify({ requested: true, }),
        success: set_hints,
    });

    function publish_event(data) {
        $.ajax({
            type: 'POST',
            url: publishUrl,
            data: JSON.stringify(data),
        });
    }

    function pre_submit() {
        problem_progress.text('(Loading...)');
    }

    function post_submit(result) {
        $xblocksContainer.data(cached_answer_id, $('.answer', element).val());
        $xblocksContainer.data(problem_progress_id, result.problem_progress);
        $xblocksContainer.data(used_attempts_feedback_id, result.used_attempts_feedback);
        problem_progress.text(result.problem_progress);
        button_holder.addClass(result.submit_class);
        used_attempts_feedback.text(result.used_attempts_feedback);
    }

    function show_answer() {
        your_answer.css('display', 'block');
        expert_answer.css('display', 'block');
        submit_button.val('Resubmit');

    }

    function reset_answer() {
        your_answer.css('display', 'none');
        expert_answer.css('display', 'none');
        submit_button.val(submit_button_label);
    }

    function reset_hint() {
        hint_counter = 0;
        hint_div.css('display', 'none');
    }

    function show_hint() {
        hint = hints[hint_counter];
        hint_div.html(hint);
        hint_div.css('display', 'block');
        publish_event({
            event_type: 'hint_button',
            next_hint_index: hint_counter,
        });
        if (hint_counter === hints.length - 1) {
            hint_counter = 0;
        } else {
            hint_counter++;
        }
    }

    $('.submit_button', element).click(function () {
        pre_submit();
        $.ajax({
            type: 'POST',
            url: handlerUrl,
            data: JSON.stringify(
                {
                    answer: $('.answer', element).val(),
                    action: 'submit',
                }
            ),
            success: post_submit,
        });
        show_answer();
    });

    reset_button.click(function () {
        $('.answer', element).val('');
        $.ajax({
            type: 'POST',
            url: handlerUrl,
            data: JSON.stringify(
                {
                    answer: '',
                    action: 'reset',
                }
            ),
            success: post_submit,
        });
        reset_answer();
        reset_hint();
    });

    $('.hint_button', element).click(function () {
        show_hint();
    });

    if ($('.answer', element).val() !== '') {
        show_answer();
    }
    /* eslint-enable camelcase */
}
