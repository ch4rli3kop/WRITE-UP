#include<bits/stdc++.h>
using namespace std;

int main(){

    int num;
    cin >> num;

    for(int i=1; i<=num; i++){
        for(int j=0; j<num-i; j++) cout << " ";
        for(int j=0; j<i*2-1; j++) cout << "*";
        cout << endl;
    }
    for(int i=num-1; i>=1; i--){
        for(int j=0; j<num-i; j++) cout << " ";
        for(int j=0; j<i*2-1; j++) cout << "*";
        cout << endl;
    }

    return 0;
}