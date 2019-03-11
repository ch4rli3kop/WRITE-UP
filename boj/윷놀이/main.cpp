/*우리나라 고유의 윷놀이는 네 개의 윷짝을 던져서 배(0)와 등(1)이 나오는 숫자를 세어 
도, 개, 걸, 윷, 모를 결정한다. 네 개 윷짝을 던져서 나온 각 윷짝의 배 혹은 등 정보가 주어질 때 
도(배 한 개, 등 세 개), 개(배 두 개, 등 두 개), 걸(배 세 개, 등 한 개), 윷(배 네 개), 모(등 네 개) 중
 어떤 것인지를 결정하는 프로그램을 작성하라.*/
 #include <bits/stdc++.h>

using namespace std;

void func(int dbc[]){
    int value=0;
    for(int i=0; i<4; i++){
        value+=dbc[i];
    }

    if (value == 3)
        cout << "A\n";
    else if (value == 2)
        cout << "B\n";
    else if (value == 1)
        cout << "C\n";
    else if (value == 0)
        cout << "D\n";
    else
        cout << "E\n";
}

int main(){
    int dbc[3][4] = {0,};
    
    cin >> dbc[0][0] >> dbc[0][1] >> dbc[0][2] >> dbc[0][3];
    cin >> dbc[1][0] >> dbc[1][1] >> dbc[1][2] >> dbc[1][3];
    cin >> dbc[2][0] >> dbc[2][1] >> dbc[2][2] >> dbc[2][3];

    for(int i=0; i<3; i++){
        func(dbc[i]);
    }
    return 0;
}