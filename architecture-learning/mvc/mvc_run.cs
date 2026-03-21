using System;

namespace ArchitectureLearning.Mvc
{
    internal class Program
    {
        static void Main()
        {
            PrintHeader();
            Lesson1_ShowDataThroughController();
            Lesson2_ControllerChangesModel();
            Lesson3_ControllerKeepsRulesInOnePlace();
        }

        static void PrintHeader()
        {
            Console.WriteLine(new string('=', 72));
            Console.WriteLine("MVC 수업: 컨트롤러가 모델과 화면 사이를 정리하는 흐름");
            Console.WriteLine(new string('=', 72));
            Console.WriteLine();
        }

        static void Lesson1_ShowDataThroughController()
        {
            Console.WriteLine("[레슨 1] 컨트롤러를 통해 학생 카드 보여 주기");
            Console.WriteLine();

            // 민수의 현재 상태를 담은 모델을 만듭니다.
            var model = new StudentModel("민수", 82, 3);
            var view = new StudentView();
            var controller = new StudentController(model, view);

            view.PrintTitle("첫 화면");
            controller.ShowStudentCard();
            controller.ShowReviewHint();
            view.PrintBlankLine();
        }

        static void Lesson2_ControllerChangesModel()
        {
            Console.WriteLine("[레슨 2] 버튼 클릭처럼 보너스 점수와 숙제 제출 처리하기");
            Console.WriteLine();

            var model = new StudentModel("지우", 66, 1);
            var view = new StudentView();
            var controller = new StudentController(model, view);

            view.PrintTitle("변경 전");
            controller.ShowStudentCard();
            controller.ShowReviewHint();
            view.PrintBlankLine();

            controller.ApplyQuizBonus(8);
            controller.SubmitHomeworkAndShowMessage();

            view.PrintTitle("변경 후");
            controller.ShowStudentCard();
            controller.ShowReviewHint();
            view.PrintBlankLine();
        }

        static void Lesson3_ControllerKeepsRulesInOnePlace()
        {
            Console.WriteLine("[레슨 3] 규칙을 컨트롤러에 모아 두면 좋은 이유");
            Console.WriteLine();

            var model = new StudentModel("서연", 97, 5);
            var view = new StudentView();
            var controller = new StudentController(model, view);

            // 실수 예시:
            // View가 직접 Score를 120으로 바꾸면 이상한 화면이 나올 수 있습니다.
            // 하지만 Controller -> Model 메서드를 거치면 Math.Min(100, ...) 규칙이 적용됩니다.
            controller.ApplyQuizBonus(10);

            view.PrintTitle("100점을 넘기려 했지만 규칙이 지켜진 결과");
            controller.ShowStudentCard();
            view.PrintCoachMessage(
                "점수 올리기 규칙을 Model 메서드 하나에 넣어 두면, " +
                "어느 화면에서 호출해도 같은 규칙이 적용됩니다.");
            view.PrintBlankLine();
        }
    }
}
