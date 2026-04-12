locust -f locustfile.py --headless --host http://localhost:8000  --csv go --only-summary

locust -f locustfile.py --headless --host http://localhost:8001  --csv nginx --only-summary

python3 graph_results.py go_stats_history.csv nginx_stats_history.csv "Go Server" "Nginx LB"
