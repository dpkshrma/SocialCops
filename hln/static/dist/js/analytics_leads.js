$(document).ready(function(){
	// chart context
	var chart;
	var cur_chart_datatype = "date";
	var cur_chart_type = "line";
	var $chart_ele;
	var ctx;
	var datasets = [];
	var max_datasets = 5;
	var dataset_template = {
        label: "All leads",
        fillColor: "rgba(220,220,220,0.2)",
        strokeColor: "rgba(220,220,220,1)",
        pointColor: "rgba(220,220,220,1)",
        pointStrokeColor: "#fff",
        pointHighlightFill: "#fff",
        pointHighlightStroke: "rgba(220,220,220,1)",
        data: []
    }
    agg_size = {
    	"day": 30,
    	"week": 5,
    	"month": 1
    }
	var agg_data = {
		"agg_size": 4,
		"agg_type": 'date',
		"time_interval": 'week'
	};

	// sample colors for datasets
	var colors = {
		"fillColor": ["rgba(220,220,220,0.2)", "rgba(151,187,205,0.2)", ],
		"strokeColor": ["rgba(220,220,220,1)", "rgba(151,187,205,1)"],
		"pointColor": ["rgba(220,220,220,1)", "rgba(151,187,205,1)"],
		"pointHighlightStroke": ["rgba(220,220,220,1)", "rgba(151,187,205,1)"]
	}

	var update_chart =function(args){
		req_args = ['agg_type', 'agg_size', 'time_interval'];
		for(i in req_args){
			k = req_args[i];
			arg = args[k];
			if (typeof arg === "undefined") args[k] = null;
		};
		if(typeof chart === 'object')
			chart.destroy();
		get_leadcount_agg(args,{
			"data": function(leadcount_data){
				var html = '', buckets;
				buckets = leadcount_data['aggregations']['count_by_'+args['agg_type']]['buckets'];
				chart_data = {
					"labels": [],
					"data": []
				}
				for(var i in buckets){
					bucket = buckets[i];
					if("key_as_string" in bucket)
						label = bucket["key_as_string"]
					else
						label = bucket["key"]
					if(!isNaN(Date.parse(label)))
						label = moment(label, 'YYYY/MM/DD hh:mm:ss').fromNow()
					chart_data['labels'].push(label);
					chart_data['data'].push(bucket['doc_count']);
				}
				var new_dataset = $.extend(true, {}, dataset_template);
				new_dataset['data'] = chart_data['data'];
				datasets.push(new_dataset);
				var data = {
				    labels: chart_data['labels'],
				    datasets: datasets
				};
				if(cur_chart_datatype=='date'){
					$chart_ele = $("#analytics_leads .chart .areaChart");
				}else if(cur_chart_datatype=='category'){
					$chart_ele = $("#analytics_categories .chart .barChart");
				}else if(cur_chart_datatype=='reporter'){
					$chart_ele = $("#analytics_reporters .chart .barChart");
				}
				ctx = $chart_ele.get(0).getContext("2d");

				if(cur_chart_type == "line")
					chart = new Chart(ctx).Line(data);
				else if(cur_chart_type == "bar")
					chart = new Chart(ctx).Bar(data);
			},
			"beforeSend": function(data){
				$("#analytics_leads_box").children('.overlay').show();
			},
			"complete": function(data){
				$("#analytics_leads_box").children('.overlay').fadeOut();
			}
		});
	}

	var update_lead_stats = function(){
		args = {}
		get_leadcount(args, {
			"data": function(leadcount_data){
				count = leadcount_data['count'];
				$("#lead_stats .info-box-number").html(count);
			}
		});
		args = {
			"agg_type": "date",
			"agg_size": 2,
			"time_interval": "week"
		};
		get_leadcount_agg(args, {
			"data": function(leadcount_data){
				// calculate % change in leads
				buckets = leadcount_data['aggregations']['count_by_date']['buckets'];
				change = buckets[1]['doc_count'] - buckets[0]['doc_count'];
				percent_change = Math.abs((parseFloat(change)/buckets[0]['doc_count'])*100);
				// rounding off
				percent_change = Math.round(percent_change*100)/100.0;
				var info_text = "";
				if(change>0){
					info_text = percent_change+"% increase "
					info_text_desc = info_text+"<i class='fa fa-arrow-up'></i>";
				}else{
					info_text = percent_change+"% decrease "
					info_text_desc = info_text+"<i class='fa fa-arrow-down'></i>";
				}
				$("#lead_stats .progress-description").html(info_text_desc);
				$("#lead_stats .progress-bar").css("width", Math.round(percent_change));
				$("#lead_stats .progress-description").attr("title",info_text+" from last week")
			}
		});
	}

	var update_reporter_stats = function(){
		args = {}
		get_reportercount(args, {
			"data": function(leadcount_data){
				count = leadcount_data['count'];
				$("#reporter_stats .info-box-number").html(count);
			}
		});
	};


	update_lead_stats();
	update_reporter_stats();
	update_chart(agg_data);

	$('#analytics_leads .time_interval').on('change', function(){
		datasets = [];
		time_interval = $(this).val();
		agg_data['agg_size'] = agg_size[time_interval];
		agg_data['time_interval'] = time_interval;
		update_chart(agg_data);
	});

	$(".chart_select #chart_time").click(function(e){
		e.preventDefault();
		if(cur_chart_datatype!='date'){
			datasets = [];
			cur_chart_datatype='date';
			cur_chart_type='line';
			$("#analytics_categories").hide();
			$("#analytics_leads").fadeIn();
			agg_data['agg_type'] = 'date';
			update_chart(agg_data);
		}
	});

	$(".chart_select #chart_category").click(function(e){
		if(cur_chart_datatype!='category'){
			datasets = [];
			cur_chart_datatype='category';
			cur_chart_type='bar';
			$("#analytics_leads").hide();
			$("#analytics_categories").fadeIn();
			agg_data['agg_type'] = 'category';
			agg_data['agg_size'] = 10;
			update_chart(agg_data);
		}
	});

	$(".nav-tabs .reporters_tab").click(function(e){
		if(cur_chart_datatype!='reporter'){
			datasets = [];
			cur_chart_type='bar';
			agg_data['agg_type'] = "reporter";
			agg_data['agg_size'] = 10;
			cur_chart_datatype = "reporter";
			update_chart(agg_data);
		}
	});

	$(".nav-tabs .leads_tab").click(function(e){
		datasets = [];
		cur_chart_type='line';
		agg_data['agg_type'] = "date";
		cur_chart_datatype = "date";
		update_chart(agg_data);
	});

});