echo "Running load balancer test on GO server"
locust -f locustfile.py --headless --host http://localhost:8000  --csv go --only-summary
echo "Sleeping for 10 seconds to ensure all data is flushed"
# wait 10 seconds to ensure all data is flushed
sleep 10

echo "Running load balancer test on Nginx"
locust -f locustfile.py --headless --host http://localhost:8001  --csv nginx --only-summary
python3 graph_results.py go_stats_history.csv nginx_stats_history.csv "Go Server" "Nginx"
