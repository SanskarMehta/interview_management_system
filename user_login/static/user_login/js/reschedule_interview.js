$(document).on('change','#date', function(){
    var date = $(this).val()
    var today = new Date();
    var current_date = today.getFullYear()+'-'+(today.getMonth()+1)+'-'+today.getDate();
    console.log(date)
    console.log(current_date)
    if (date<=current_date){
        alert('Invalid Date Input')
    }
    else{
            console.log(date)
    }
})
