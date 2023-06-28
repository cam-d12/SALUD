#include <iostream>
#include <fstream>
// #include <string>
#include <queue>
#include <vector>
#include <algorithm>

using namespace std;

struct Process {
    int id;
    int arrival_time;
    int burst;
    int priority;
};

struct ComparePriority {
    bool operator()(Process const& p1, Process const& p2) {
        return p1.priority > p2.priority;
    }
};

struct CompareBurst {
    bool operator()(Process const& p1, Process const& p2) {
        return p1.burst > p2.burst;
    }
};

vector<Process> readFile(string filename) {
    vector<Process> processes;
    ifstream file(filename);

    if (!file) {
        cout << "ERROR: Cannot read file.";
        return processes;
    }

    string line;
    while (getline(file, line)) {
        // istringstream iss(line);
        Process process;

        processes.push_back(process);
    }

    file.close();
    return processes;
}

void FCFS(vector<Process> processes){
    sort(processes.begin(), processes.end(), [](const Process& a, const Process& b) {
        return a.arrival_time < b.arrival_time;
    });
    
    int totalTurnaroundTime = 0, totalWaitingTime = 0, currentTime = 0;
    for (const Process& process : processes){
        if (currentTime < process.arrival_time){
            currentTime = process.arrival_time;
        }

        int waitingTime = currentTime - process.arrival_time;
        totalWaitingTime += waitingTime;

        int turnaroundTime = waitingTime - process.burst;
        totalTurnaroundTime += turnaroundTime;

        currentTime += process.burst;
    }

    double avgTurnaroundTime = totalTurnaroundTime/processes.size();
    double avgWaitingTime = totalWaitingTime/processes.size();
    double throughput = processes.size()/currentTime;

    cout << "---FCFS---" << "\n";
    cout << "Average Turnaround Time: " << avgTurnaroundTime << "\n";
    cout << "Average Waiting Time: " << avgWaitingTime << "\n";
    cout << "Throughput: " << throughput << "\n";
}

void SJFP(vector<Process> processes){
    sort(processes.begin(), processes.end(), [](const Process& a, const Process& b) {
        return a.arrival_time < b.arrival_time;
    });
    

    priority_queue<Process, vector<Process>, CompareBurst> pq;
    int totalTurnaroundTime = 0, totalWaitingTime = 0, currentTime = 0;
    size_t index = 0;

    while (!pq.empty() || index < processes.size()) {
        while (index < processes.size() && processes[index].arrival_time <= currentTime) {
            pq.push(processes[index]);
            index++;
        }

        if (!pq.empty()) {
            Process process = pq.top();
            pq.pop();

            if (currentTime < process.arrival_time) {
                currentTime = process.arrival_time;
            }

            int waitingTime = currentTime - process.arrival_time;
            totalWaitingTime += waitingTime;

            int turnaroundTime = waitingTime - process.burst;
            totalTurnaroundTime += turnaroundTime;

            currentTime += process.burst;
        } else {
            currentTime = processes[index].arrival_time;
        }
    }

    
    double avgTurnaroundTime = totalTurnaroundTime/processes.size();
    double avgWaitingTime = totalWaitingTime/processes.size();
    double throughput = processes.size()/currentTime;

    cout << "---SJFP---" << "\n";
    cout << "Average Turnaround Time: " << avgTurnaroundTime << "\n";
    cout << "Average Waiting Time: " << avgWaitingTime << "\n";
    cout << "Throughput: " << throughput << "\n";
}

void Priority(vector<Process> processes){
    sort(processes.begin(), processes.end(), [](const Process& a, const Process& b) {
        return a.arrival_time < b.arrival_time;
    });
    

    priority_queue<Process, vector<Process>, ComparePriority> pq;
    int totalTurnaroundTime = 0, totalWaitingTime = 0, currentTime = 0;
    size_t index = 0;

    while (!pq.empty() || index < processes.size()) {
        while (index < processes.size() && processes[index].arrival_time <= currentTime) {
            pq.push(processes[index]);
            index++;
        }

        if (!pq.empty()) {
            Process process = pq.top();
            pq.pop();

            if (currentTime < process.arrival_time) {
                currentTime = process.arrival_time;
            }

            int waitingTime = currentTime - process.arrival_time;
            totalWaitingTime += waitingTime;

            int turnaroundTime = waitingTime - process.burst;
            totalTurnaroundTime += turnaroundTime;

            currentTime += process.burst;
        } else {
            currentTime = processes[index].arrival_time;
        }
    }

    double avgTurnaroundTime = totalTurnaroundTime/processes.size();
    double avgWaitingTime = totalWaitingTime/processes.size();
    double throughput = processes.size()/currentTime;

    cout << "---Priority---" << "\n";
    cout << "Average Turnaround Time: " << avgTurnaroundTime << "\n";
    cout << "Average Waiting Time: " << avgWaitingTime << "\n";
    cout << "Throughput: " << throughput << "\n";
}


int main(int argc, char *argv[]){
    if (argc != 2) {
        cout << "ERROR: should only take one input file.";
        return 1;
    }

    string filename = argv[1];
    vector<Process> processes = readFile(filename);

    FCFS(processes);
    SJFP(processes);
    Priority(processes);

    return 0;
}