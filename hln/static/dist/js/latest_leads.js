$(document).ready(function(){
	// latest leads query data
	var ll_data = {
		"search_query": "",
		"count": 5,
		"offset": 0
	};

	var update_latest_leads = function(args){
		req_args = ['search_query', 'count', 'offset'];
		for(i in req_args){
			k = req_args[i];
			arg = args[k];
			if (typeof arg === "undefined") args[k] = null;
		};
		get_leads(args,{
			// get_leads output handler functions
			"data": function(lead_data){
				var html = '', hit_src;
				for (var i = 0; i < lead_data.hits.hits.length; i++) {
					hit_src = lead_data.hits.hits[i]['_source'];
					// get reporter of the lead
					d= {
						'lead_text': hit_src['data']['text'],
						'reporter_name': hit_src['reporter']['name'],
						'lead_time_relative': moment(hit_src['created_at'], 'YYYY/MM/DD hh:mm:ss').fromNow(),
						'lead_time': hit_src['created_at'],
						'reporter_img_src': hit_src['reporter']['profile_image_url']
					};
					var lead_html = new EJS({url: '/dist/partials/lead.ejs'}).render(d);
					html += lead_html;
				};
				$('#latest_leads .box-body').html(html);
			},
			"beforeSend": function(data){
				$("#latest_leads .overlay").show();
			},
			"complete": function(data){
				$("#latest_leads .overlay").fadeOut();
			}
		});
	};

	// load latest lead on pageload
	update_latest_leads(ll_data);

	$("#latest_leads .search_query").keypress(function (e) {
	    if (e.keyCode == 13) {
	    	search_query = $('#latest_leads .search_query').val();
	    	if (search_query.length) {
	    		ll_data['search_query'] = search_query;
		    	update_latest_leads(ll_data);
	    	};
	    }
	});

	// latest_leads pagination
	$("#latest_leads .pagination li a").click(function(e){
		e.preventDefault();
		var page_num = $(this).attr('data-pagenum');
		if(isNaN(parseInt(page_num))){
			if (page_num=='b' && ll_data['offset']!=0) {
				ll_data['offset'] -= 1;
			}else{
				ll_data['offset'] += 1;
			};
		}else{
			ll_data['offset'] = parseInt(page_num)-1;
		}
		update_latest_leads(ll_data);
		$("#latest_leads .pagination li").removeClass("active");
		$("#latest_leads .pagination li a[data-pagenum="+(ll_data['offset']+1)+"]").parent().addClass("active");
	});
});