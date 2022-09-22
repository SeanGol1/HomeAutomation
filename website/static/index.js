function deleteNote(noteId) {
    fetch('delete-note', {
        method: "POST",
        body: JSON.stringify({ noteId: noteId})
    }).then((_res) => {
        window.location.href = "members_area";
    });
}

function deletePubnote(noteId) {
    fetch('delete-pubnote', {
        method: "POST",
        body: JSON.stringify({ noteId: noteId})
    }).then((_res) => {
        window.location.href = "public_notes";
    });
}

 function commentPubnote(noteId) {
     var comment = document.getElementById("pubcom"+noteId).value;
     fetch('comment-pubnote',{
         method: "POST",
         body: JSON.stringify({ noteId: noteId, comment: comment})
     }).then((_res) => {
        window.location.href = "public_notes";
    });
}

 $(document).ready(function(){
    // Check Radio-box
    $(".rating input:radio").attr("checked", false);

    $('.rating input').click(function () {
        $(".rating span").removeClass('checked');
        $(this).parent().addClass('checked');
    });

    $('input:radio').change(
      function(){
        var userRating = this.value;
        var noteId = $("input:radio").parent().attr('id');
        fetch('rate-pubnote',{
            method: "POST",
            body: JSON.stringify({ noteId: noteId, rating: userRating})
        }).then((_res) => {
            window.location.href = "public_notes";
            alert(noteId);
        });
    }); 
   $('#recent_show').on('click', function(e) {
        e.preventDefault()
        fetch('recent_show',{
            method: "POST",
        }).then((_res) => {
        });
        return false;
    });
    $('#lampbright').on('click', function(e) {
        e.preventDefault()
        fetch('lampbright',{
            method: "POST",
        }).then((_res) => {
        });
        return false;
    });
    $('#lampswitch').on('click', function(e) {
        e.preventDefault()
        fetch('lampswitch',{
            method: "POST",
        }).then((_res) => {
        });
        return false;
    });
    $('#moodlight').on('click', function(e) {
        e.preventDefault()
        fetch('moodlight',{
            method: "POST",
        }).then((_res) => {
        });
        return false;
    });
    $('#lightbright').on('click', function(e) {
        e.preventDefault()
        fetch('lightbright',{
            method: "POST",
        }).then((_res) => {
        });
        return false;
    });
    $('#lightswitch').on('click', function(e) {
        e.preventDefault()
        fetch('lightswitch',{
            method: "POST",
        }).then((_res) => {
        });
        return false;
    });
    
    $('#hallbright').on('click', function(e) {
        e.preventDefault()
        fetch('hallbright',{
            method: "POST",
        }).then((_res) => {
        });
        return false;
    });
    $('#hallswitch').on('click', function(e) {
        e.preventDefault()
        fetch('hallswitch',{
            method: "POST",
        }).then((_res) => {
        });
        return false;
    });
    
    $('#lightsoff').on('click', function(e) {
        e.preventDefault()
        fetch('lightsoff',{
            method: "POST",
        }).then((_res) => {
        });
        return false;
    });

    $('#next_episode').on('click', function(e) {
        e.preventDefault()
        fetch('next_episode',{
            method: "POST",
        }).then((_res) => {
        });
        return false;
    });
    $('#spotify').on('click', function(e) {
        e.preventDefault()
        fetch('spotify',{
            method: "POST",
        }).then((_res) => {
        });
        return false;
    });
    $('#playpause').on('click', function(e) {
        e.preventDefault()
        fetch('playpause',{
            method: "POST",
        }).then((_res) => {
        });
        return false;
    });
    
    $('#poweroff').on('click', function(e) {
        e.preventDefault()
        fetch('poweroff',{
            method: "POST",
        }).then((_res) => {
        });
        return false;
    });
     
    $('#formula1').on('click', function(e) {
        e.preventDefault()
        fetch('formula1',{
            method: "POST",
        }).then((_res) => {
        });
        return false;
    });

    $('#wakeup').on('click', function(e) {
        e.preventDefault()
        fetch('wakeup',{
            method: "POST",
        }).then((_res) => {
        });
        return false;
    });
          
     
});
