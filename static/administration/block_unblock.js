$(document).ready(function(){
    $('.block_status').click(function(){
        var user_id = $(this).attr('data-user_id')
        var data_status = $(this).attr('data-status')
        if (data_status==='1'){
            let message = prompt("Please Enter why you want to block the user");
            if(message === "" || message === null){
                alert('Please enter something');
            }
            else{
                data = {'user_id':user_id,'data_status':data_status,'message':message}
                console.log(data);
                $.ajax({
                    type:"POST",
                    data : JSON.stringify(data),
                    url:"/administration/block_unblock/",
                    success:function(response){
                        alert("Thank you.......")
                    }
                })
            }
        }
        else{
            data = {'user_id':user_id,'data_status':data_status}
            console.log(data);
            $.ajax({
                type:"POST",
                data : JSON.stringify(data),
                url:"/administration/block_unblock/",
                success:function(response){
                    alert("Thank you.......")
                }
            })
        }
    })
})