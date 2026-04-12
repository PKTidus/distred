echo "Running load balancer test on GO server"
locust -f locustfile.py --headless --host http://34.106.186.215  --csv go_remote --only-summary
echo "Sleeping for 10 seconds to ensure all data is flushed"
echo "Press Enter to continue..."
read -r _ 
echo "Running load balancer test on Nginx"
locust -f locustfile.py --headless --host http://34.106.167.51  --csv nginx_remote --only-summary
python3 graph_results.py go_remote_stats_history.csv nginx_remote_stats_history.csv "Go Server" "Nginx"
