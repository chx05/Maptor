#include "pub/editor.c"

int32_t main()
{
    mpt_t maptor;

    mpt_init(&maptor, 800, 600);
    {
        mpt_run(&maptor);
    }
    mpt_deinit(&maptor);

    return 0;
}
