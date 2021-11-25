let commissionType = '';

// update the commission type
updateCommission = (type) => {
    commissionType = type;
}

// sell bitcoin
sell_bitcoin = (clientId, membership_type) => {

    let bit_sell = $('#sell_bitcoin_value').val();
    let available = parseFloat($('#bitcoin_units_owned').text().split(":")[1].trim());

    if (commissionType == '') {
        alert("Please select the commission type from profile tab");
        return;
    }

    if (isNaN(bit_sell) || bit_sell === '') {
        alert("Please enter proper inputs");
        return;
    }

    if (bit_sell > available) {
        alert("You are trying to sell more than you own.");
    } else {
        let data = {
            ClientId: clientId,
            MembershipType: membership_type,
            BitcoinSell : bit_sell,
            CommissionType:commissionType,
        }
        $.ajax({
            type: "POST",
            url: "http://127.0.0.1:5000/sell_bitcoin",
            data: JSON.stringify(data),// now data come in this function
            contentType: "application/json; charset=utf-8",
            crossDomain: true,
            dataType: "json",
            success: function (data, status, jqXHR) {
                window.location.reload(true);
            }, error: function (jqXHR, status) {
                alert('fail, you have pending transactions left.');
            }
        });
    }
}

// buy bitcoin
buy_bitcoin = (recipient_id, membership_type, client_id, bitcoin_val) => {
    let bit_sell = $('#buy_bitcoin_value').val();

    if (bit_sell === '' || isNaN(bit_sell)) {
        alert("Please enter proper inputs");
        return;
    }

    if (bit_sell > bitcoin_val) {
        alert("You are trying to buy more than person is selling");
    } else {
        let data = {
            ClientId: recipient_id,
            MembershipType: membership_type,
            BitcoinBuy : bit_sell,
            RecipientId: client_id,
            TransactionId: Math.random().toString(36).substr(2, 12),
            CommissionType:commissionType,
        }
        $.ajax({
            type: "POST",
            url: "http://127.0.0.1:5000/buy_bitcoin",
            data: JSON.stringify(data),// now data come in this function
            contentType: "application/json; charset=utf-8",
            crossDomain: true,
            dataType: "json",
            success: function (data, status, jqXHR) {
                window.location.reload(true);
            }, error: function (jqXHR, status) {
                alert('fail, you have pending transactions left.');
            }
        });
    }
}