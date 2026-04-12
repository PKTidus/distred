locust -f locustfile.py --headless --host http://34.106.186.215  --csv go_remote --only-summary

locust -f locustfile.py --headless --host http://34.106.167.51  --csv nginx_remote --only-summary

python3 graph_results.py go_remote_stats_history.csv nginx_remote_stats_history.csv "Go Server" "Nginx LB"
