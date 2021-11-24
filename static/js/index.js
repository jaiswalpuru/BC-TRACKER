sell_bitcoin = (clientId, membership_type) => {

    let bit_sell = $('#sell_bitcoin_value').val();
    let available = parseFloat($('#bitcoin_units_owned').text().split(":")[1].trim());

    if (isNaN(bit_sell)) {
        alert("Please enter proper inputs");
        return
    }

    if (bit_sell > available) {
        alert("You are trying to sell more than you own.");
    } else {
        let data = {
            ClientId: clientId,
            TransactionId: Math.random().toString(36).substr(2, 12),
            TransactionType: 'SELL',
            MembershipType: membership_type,
            BitcoinSell : bit_sell,
        }
        $.ajax({
            type: "POST",
            url: "http://127.0.0.1:5000/sell_transaction",
            data: JSON.stringify(data),// now data come in this function
            contentType: "application/json; charset=utf-8",
            crossDomain: true,
            dataType: "json",
            success: function (data, status, jqXHR) {
                window.location.reload(true);
            },
            error: function (jqXHR, status) {
                console.log(jqXHR);
                alert('fail' + status.code);
            }
        });
    }
}