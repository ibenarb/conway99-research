#define main research_main
#include "residual_gram_v1.cpp"
#undef main
int main(int argc, char **argv) {
    try {
        if (argc != 2) throw runtime_error("Expected setup filename");
        read_setup(argv[1]);
        Choice x{}, y{};
        while (cin >> x.attachment >> x.support >> x.signs >> y.attachment >> y.support >> y.signs) {
            if (x.attachment < 0 || x.attachment >= int(attachments.size()) ||
                y.attachment < 0 || y.attachment >= int(attachments.size()))
                throw runtime_error("Invalid attachment index");
            cout << allowed_cross(x,y) << "\n";
        }
        return 0;
    } catch (const exception &e) { cerr << e.what() << endl; return 2; }
}
