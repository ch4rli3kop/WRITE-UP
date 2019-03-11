#include<bits/stdc++.h>
using namespace std;

int main(){

    string str = "**************************************";
    int num;

    cin >> num;

    for(int i=num; i>=1; i--){
        for(int j=0; j<i; j++)
            cout << "*";
        cout << endl;
    }
    return 0;
}