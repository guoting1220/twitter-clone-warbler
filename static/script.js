$(async function () {   
    $("#messages").on('click', 'button', async function(e){
        e.preventDefault()
        const $tgt = $(e.target);
        const btnId = $tgt.attr("id");
     
        const response = await axios.post(`/messages/${btnId}/like`);   
        console.log(response);  
        if (response.data.result === "unlike") {
            $tgt.addClass("btn-secondary");
            $tgt.removeClass("btn-primary");
        } else if (response.data.result === "like") {
            $tgt.removeClass("btn-secondary");
            $tgt.addClass("btn-primary");
        }
    })
})