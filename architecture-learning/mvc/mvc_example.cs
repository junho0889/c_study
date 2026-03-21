using System;

namespace ArchitectureLearning.Mvc
{
    /*
      MVC에서 Model은 "학생 카드" 자체입니다.
      이름, 점수, 숙제 개수처럼 진짜 데이터가 들어 있습니다.

      비유:
      - Model = 공책
      - View = 공책 내용을 화면에 보여 주는 칠판
      - Controller = 선생님처럼 "점수 올려", "숙제 하나 추가" 같은 지시를 받아서
                     공책을 고치고 칠판을 다시 보여 주는 사람
    */
    public class StudentModel
    {
        public string Name { get; private set; }
        public int Score { get; private set; }
        public int HomeworkCount { get; private set; }

        public StudentModel(string name, int score, int homeworkCount)
        {
            Name = name;
            Score = score;
            HomeworkCount = homeworkCount;
        }

        public void AddBonusScore(int bonus)
        {
            // 점수는 100점을 넘지 않게 잘라 줍니다.
            // 게임에서 체력이 100을 넘지 않게 막는 것과 같은 생각입니다.
            Score = Math.Min(100, Score + bonus);
        }

        public void SubmitHomework()
        {
            HomeworkCount += 1;
        }

        public bool NeedsReview()
        {
            return Score < 70;
        }
    }

    /*
      View는 계산을 거의 하지 않고 "보여 주는 일"에 집중합니다.
      초보자가 자주 하는 실수는 View에서 점수 계산까지 다 해 버리는 것인데,
      그러면 화면이 바뀔 때마다 규칙이 여러 군데 흩어져서 고치기 어려워집니다.
    */
    public class StudentView
    {
        public void PrintTitle(string title)
        {
            Console.WriteLine(title);
            Console.WriteLine(new string('-', title.Length));
        }

        public void PrintStudentCard(StudentModel model)
        {
            Console.WriteLine($"이름: {model.Name}");
            Console.WriteLine($"점수: {model.Score}");
            Console.WriteLine($"제출한 숙제 수: {model.HomeworkCount}");
        }

        public void PrintCoachMessage(string message)
        {
            Console.WriteLine("설명: " + message);
        }

        public void PrintBlankLine()
        {
            Console.WriteLine();
        }
    }

    /*
      Controller는 버튼 클릭, 폼 제출 같은 "행동"을 받아서
      Model을 바꾸고 View에게 다시 보여 달라고 부탁합니다.

      왜 필요한가?
      - View가 직접 Model을 막 바꾸기 시작하면
        "누가 언제 점수를 바꿨는지" 찾기 어려워집니다.
      - Controller를 거치면 흐름이 한 줄로 정리됩니다.
    */
    public class StudentController
    {
        private readonly StudentModel _model;
        private readonly StudentView _view;

        public StudentController(StudentModel model, StudentView view)
        {
            _model = model;
            _view = view;
        }

        public void ShowStudentCard()
        {
            _view.PrintStudentCard(_model);
        }

        public void ApplyQuizBonus(int bonus)
        {
            _model.AddBonusScore(bonus);
            _view.PrintCoachMessage($"퀴즈 보너스 {bonus}점을 더했습니다.");
        }

        public void SubmitHomeworkAndShowMessage()
        {
            _model.SubmitHomework();
            _view.PrintCoachMessage("숙제 한 개를 제출해서 숙제 개수가 1 늘었습니다.");
        }

        public void ShowReviewHint()
        {
            if (_model.NeedsReview())
            {
                _view.PrintCoachMessage("아직 70점 미만이라서 복습이 더 필요합니다.");
            }
            else
            {
                _view.PrintCoachMessage("70점 이상이므로 다음 단원으로 넘어가도 됩니다.");
            }
        }
    }
}
