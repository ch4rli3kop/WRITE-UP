/*
문제

1에서부터 6까지의 눈을 가진 3개의 주사위를 던져서 다음과 같은 규칙에 따라 상금을 받는 게임이 있다. 

규칙(1) 같은 눈이 3개가 나오면 10,000원+(같은 눈)*1,000원의 상금을 받게 된다. 

규칙(2) 같은 눈이 2개만 나오는 경우에는 1,000원+(같은 눈)*100원의 상금을 받게 된다. 

규칙(3) 모두 다른 눈이 나오는 경우에는 (그 중 가장 큰 눈)*100원의 상금을 받게 된다.  

예를 들어, 3개의 눈 3, 3, 6이 주어지면 상금은 1,000+3*100으로 계산되어 1,300원을 받게 된다. 또 3개의 눈이 2, 2, 2로 주어지면 10,000+2*1,000 으로 계산되어 12,000원을 받게 된다. 3개의 눈이 6, 2, 5로 주어지면 그중 가장 큰 값이 6이므로 6*100으로 계산되어 600원을 상금으로 받게 된다.

3개 주사위의 나온 눈이 주어질 때, 상금을 계산하는 프로그램을 작성 하시오.
입력

첫 째 줄에 3개의 눈이 빈칸을 사이에 두고 각각 주어진다. 
출력

첫째 줄에 게임의 상금을 출력 한다.  
*/

// 아이디어 : 같은 값의 개수를 셀 때, 정렬한 뒤에 세기
#include <bits/stdc++.h>
#include <vector>
#include <algorithm>

using namespace std;

void parsingVector (vector<int> &dice, vector< vector<int> > &count_value){
    int vect_lenght = dice.size();
    int count=0;
    vector<int> v(2);

    for(int i=0; i<vect_lenght; i++){
        count++;
        if (dice[i] != dice[i+1] || i == vect_lenght-1){  //  정렬된 dice 벡터에서 새로운 값을 만난 경우와 마지막일 경우
            v[0] = count;
            v[1] = dice[i];
            count_value.push_back(v);  //  생성한 벡터를 count_value에 추가
            count = 0;  //  count 초기화
        }
    }
}

bool compare(vector<int> v1, vector<int> v2){
    if (v1[0] == v2[0])  // v1[0]와 v2[0]가 같을 경우
        return v1[1] > v2[1];  // v1[1]과 v2[1]을 내림차순으로 정렬
    else
        return v1[0] > v2[0];  // v1[0]과 v2[0]을 내림차순으로 정렬
}


int main(){

    vector<int> dice(3);
    vector< vector<int> > count_value;
    int reward = 0;

    cin >> dice[0] >> dice[1] >> dice[2];

    sort(dice.begin(), dice.end(), greater<int>());  // dice 벡터를 내림차순으로 정렬
    parsingVector(dice, count_value);  //  dice 벡터를 파싱하여 count_value 이중 벡터에 개수:값 형태로 저장
    sort(count_value.begin(), count_value.end(), compare);  //  개수, 값 순서로 내림차순으로 count_value를 정렬
   
    switch(count_value[0][0]){
        case 3:
            reward = 10000 + count_value[0][1]*1000;
            break;
        case 2:
            reward = 1000 + count_value[0][1]*100;
            break;
        case 1:
            reward = count_value[0][1]*100;
            break;
        default:
            cout << "error!" << endl;
            exit(1);
    }

    cout << reward;

    return 0;
}