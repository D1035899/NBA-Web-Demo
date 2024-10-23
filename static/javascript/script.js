$(document).ready(function () {

    $(".team-select").select2({
        placeholder: "請選擇球隊",
        allowClear: true,
        width: "100%",
        language: {
            noResults: function () {
                return "找不到符合的球隊";
            },
        },
        // templateResult: formatPlayer,
        // templateSelection: formatPlayerSelection,
        // matcher: matchCustom,
    });
    $(".player-select").select2({
        placeholder: "請選擇5位球員",
        allowClear: true,
        width: "100%",
        language: {
            noResults: function () {
                return "找不到符合的球員";
            },
        },
        closeOnSelect: true,
        maximumSelectionLength: 5,
        // templateResult: formatPlayer,
        // templateSelection: formatPlayerSelection,
        matcher: matchCustom,
    });

    // 如果要在選項顯示id
    // function formatPlayer(player) {
    //     if (!player.id) {
    //         return player.text;
    //     }
    //     var playerName = $(player.element).data("name");
    //     return playerName ? `${playerName} (${player.id})` : player.text;
    // }

    // function formatPlayerSelection(player) {
    //     if (!player.id) {
    //         return player.text;
    //     }
    //     var playerName = $(player.element).data("name");
    //     return playerName ? playerName : player.text;
    // }

    function matchCustom(params, data) {
        if ($.trim(params.term) === "") {
            return data;
        }

        if (
            data.id.toString().indexOf(params.term) > -1 ||
            $(data.element)
                .data("name")
                .toLowerCase()
                .indexOf(params.term.toLowerCase()) > -1
        ) {
            return data;
        }

        return null;
    }

    function disableOptionInOtherSelect(selectedValues, otherSelect) {
        $(otherSelect)
            .find("option")
            .each(function () {
                if (selectedValues.includes($(this).val())) {
                    $(this).prop("disabled", true);
                } else {
                    $(this).prop("disabled", false);
                }
            });
        $(otherSelect).trigger("change.select2");
    }

    function disableOptionInAnotherTeam(selectedValue, targetSelect) {
        $(targetSelect)
            .find("option")
            .each(function () {
                if ($(this).val() === selectedValue) {
                    $(this).prop("disabled", true);
                } else {
                    $(this).prop("disabled", false);
                }
            });
        $(targetSelect).trigger("change.select2");
    }
    $("#team1Players").on("change", function () {
        var selectedValues = $(this).val() || [];
        disableOptionInOtherSelect(selectedValues, "#team2Players");
    });

    $("#team2Players").on("change", function () {
        var selectedValues = $(this).val() || [];
        disableOptionInOtherSelect(selectedValues, "#team1Players");
    });
    $("#team1").on("change", function () {
        var selectedValues = $(this).val() || [];
        disableOptionInAnotherTeam(selectedValues, "#team2");
    });
    $("#team2").on("change", function () {
        var selectedValues = $(this).val() || [];
        disableOptionInAnotherTeam(selectedValues, "#team1");
    });
});


// 判斷表單有沒有填好
$("form").on("submit", function (e) {
    var min = 5;
    var team1Players = $("#team1Players").val() || [];
    var team2Players = $("#team2Players").val() || [];
    var team1 = $("#team1").val();
    var team2 = $("#team2").val();
    if (!team1 || !team2) {
        e.preventDefault();
        alert("必須選擇兩個隊伍");
    }
    if (team1Players.length !== min || team2Players.length !== min) {
        e.preventDefault();
        alert("每個隊伍必須選擇5位球員");
    }

});
