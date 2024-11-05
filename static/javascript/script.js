$(document).ready(function () {
    // 初始化隊伍以及球員選單
    $(".team-select").select2({
        placeholder: "請選擇球隊",
        // allowClear: true,
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
        placeholder: "請先選擇球隊",
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

    // 如果要在選項顯示id, 請將該函示取消註解，並且將含有該函示名稱的地方也取消註解
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

    //更新球員名單
    function updatePlayers(teamSelectId, playersDivId) {
    const teamSelectElement = document.getElementById(teamSelectId).value;
    fetch(`/get_players/${teamSelectElement}`)
        .then((response) => response.json())
        .then((data) => {
            const playersDiv = document.getElementById(playersDivId);
            playersDiv.innerHTML = ""; // 清除現有的球員名單
            // 建立球員名單
            data.players.forEach((player) => {
                const option = document.createElement("option");
                option.setAttribute("data-name", player.name);
                option.value = player.id;
                option.innerHTML = player.name;
                playersDiv.appendChild(option);
            });

            // 更新 Select2 套件
            $(`#${playersDivId}`).select2({
                placeholder: "請選擇5位球員",
                // allowClear: true,
                width: "100%",
                language: {
                    noResults: function () {
                        return "找不到符合的球員";
                    },
                },
                closeOnSelect: true,
                maximumSelectionLength: 5,
            });
        })
        .catch((error) => {
            console.error('Error fetching players:', error);
        });
}

    //建立球員搜尋欄的搜尋規則
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

    // 若其中一個球員被選走，則隔壁選單的該球員要被disabled
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

    // 若其中一個隊伍被選走，則隔壁選單的該隊伍要被disabled
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

    // 偵測球員是否被選取
    $("#team1Players").on("change", function () {
        var selectedValues = $(this).val() || [];
        disableOptionInOtherSelect(selectedValues, "#team2Players");
    });

    // 偵測球員是否被選取
    $("#team2Players").on("change", function () {
        var selectedValues = $(this).val() || [];
        disableOptionInOtherSelect(selectedValues, "#team1Players");
    });

    // 偵測主場隊伍是否被選取，並且根據選取的隊伍新增球員名單
    $("#team1").on("change", function () {
        const playerSelect = document.getElementById("team1Players");
        playerSelect.removeAttribute("disabled");
        var selectedValues = $(this).val() || [];
        disableOptionInAnotherTeam(selectedValues, "#team2");
        updatePlayers("team1", "team1Players");
    });

    // 偵測客場隊伍是否被選取，並且根據選取的隊伍新增球員名單
    $("#team2").on("change", function () {
        const playerSelect = document.getElementById("team2Players");
        playerSelect.removeAttribute("disabled");
        var selectedValues = $(this).val() || [];
        disableOptionInAnotherTeam(selectedValues, "#team1");
        updatePlayers("team2", "team2Players");
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
