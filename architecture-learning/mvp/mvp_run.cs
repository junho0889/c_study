using System;

namespace ArchitectureLearning.Mvp
{
    public class ConsoleStudentView : IStudentView
    {
        public void ShowTitle(string title)
        {
            Console.WriteLine(title);
            Console.WriteLine(new string('-', title.Length));
        }

        public void ShowStudentCard(string summary)
        {
            Console.WriteLine(summary);
        }

        public void ShowHint(string message)
        {
            Console.WriteLine("설명: " + message);
        }

        public void ShowBlankLine()
        {
            Console.WriteLine();
        }
    }

    internal class Program
    {
        static void Main()
        {
            PrintHeader();
            Lesson1_PresenterFormatsTheMessage();
            Lesson2_PresenterHandlesRetestLogic();
            Lesson3_ViewStaysVerySimple();
        }

        static void PrintHeader()
        {
            Console.WriteLine(new string('=', 72));
            Console.WriteLine("MVP 수업: 프레젠터가 화면용 문장을 책임지는 흐름");
            Console.WriteLine(new string('=', 72));
            Console.WriteLine();
        }

        static void Lesson1_PresenterFormatsTheMessage()
        {
            Console.WriteLine("[레슨 1] Presenter가 모델을 읽어 화면용 문장 만들기");
            Console.WriteLine();

            var model = new StudentModel("유진", 68, 2);
            var view = new ConsoleStudentView();
            var presenter = new StudentPresenter(model, view);

            view.ShowTitle("첫 출력");
            presenter.PresentStudentCard();
            view.ShowBlankLine();
        }

        static void Lesson2_PresenterHandlesRetestLogic()
        {
            Console.WriteLine("[레슨 2] 재시험 점수 반영 후 다시 화면 갱신하기");
            Console.WriteLine();

            var model = new StudentModel("하린", 63, 1);
            var view = new ConsoleStudentView();
            var presenter = new StudentPresenter(model, view);

            view.ShowTitle("재시험 전");
            presenter.PresentStudentCard();
            view.ShowBlankLine();

            view.ShowTitle("재시험 후");
            presenter.ApplyRetestAndRefresh(12);
            view.ShowBlankLine();
        }

        static void Lesson3_ViewStaysVerySimple()
        {
            Console.WriteLine("[레슨 3] View를 단순하게 두면 좋은 이유");
            Console.WriteLine();

            var model = new StudentModel("도윤", 88, 0);
            var view = new ConsoleStudentView();
            var presenter = new StudentPresenter(model, view);

            presenter.PresentStudentCard();
            view.ShowHint(
                "ConsoleStudentView는 받은 문자열을 출력만 합니다. " +
                "점수 기준, 숙제 판단, 조언 문장 조합은 Presenter가 맡습니다.");
            view.ShowBlankLine();
        }
    }
}
