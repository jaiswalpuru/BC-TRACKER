let commissionType = '';

// update the commission type
updateCommission = (type) => {
    commissionType = type;
}

manage_money = (current_bal) => {
    let amt_move = $('#amt_move').val();
    let url = "http://127.0.0.1:5000/"
    let manage_credit = document.getElementById('credit_radio').checked;
    let manage_debit = document.getElementById('debit_radio').checked;

    if (manage_credit === true) {
        url += 'credit_balance';
    }

    if (manage_debit === true) {
        url += 'debit_balance';
    }

    let data = {
        credit_amt:amt_move,
        cur_balance:current_bal,
    }

    $.ajax({
        type:"POST",
        url:url,
        data : JSON.stringify(data),
        contentType: "application/json; charset=utf-8",
        crossDomain:true,
        dataType:"json",
        success: (data, status, jqXHR) => {
            if (data.success) {
                window.location.reload();
            } else {
                alert("Invalid amount");
            }
            //window.location.reload();
        }, error:(jqXHR, status) => {
            alert("Money transfer failed");
        }
    });
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
            success: (data, status, jqXHR) => {
                if (data['success'] === false) {
                    alert("You have pending transactions left");
                } else {
                    window.location.reload(true);
                }
            }, error: (jqXHR, status) => {
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
            success:  (data, status, jqXHR) => {
                if (data['success']===false) {
                    alert("You have pending transactions left");
                } else {
                    window.location.reload(true);
                }
            }, error: (jqXHR, status) => {
                alert('fail, you have pending transactions left.');
            }
        });
    }
}

get_bitcoin_rate = () => {
    $.ajax({
        type:"GET",
        url:'http://127.0.0.1:5000/get_bit_rate',
        contentType: "application/json; charset=utf-8",
        crossDomain:true,
        dataType:"json",
        success: (data, status, jqXHR) => {
            alert("Current Bitcoin rate : " + data.curr_rate);
        }, error:(jqXHR, status) => {
            alert("Money transfer failed");
        }
    });
}

manage_bitcoin = (cur_bitcoin) => {
    let amt = $('#bit_move').val();
    let url = '';

    let manage_credit_bit = document.getElementById('credit_radio_bit').checked;
    let manage_debit_bit = document.getElementById('debit_radio_bit').checked;

    if (manage_credit_bit === true) {
        url += 'credit_bitcoin';
    }

    if (manage_debit_bit === true) {
        url += 'debit_bitcoin';
    }

    let data = {
        bitcoin:amt,
        curr_bitcoin:cur_bitcoin,
    }

    $.ajax({
        type:"POST",
        url:url,
        data : JSON.stringify(data),
        contentType: "application/json; charset=utf-8",
        crossDomain:true,
        dataType:"json",
        success: (data, status, jqXHR) => {
            if (data.success) {
                window.location.reload();
            } else {
                alert("Invalid amount");
            }
            //window.location.reload();
        }, error:(jqXHR, status) => {
            alert("Money transfer failed");
        }
    });

    return;
}

buy_ether = () => {

}