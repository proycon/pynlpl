#include <string>

#include <boost/python.hpp>
using namespace boost::python;

#include "srilm/include/File.h"
#include "srilm/include/Ngram.h"
#include "srilm/include/Vocab.h"
//#include <NgramStats.h>
#include "srilm/lm/src/NgramStatsLong.cc"

class LanguageModel
{
private:
	Vocab vocab;
	Ngram model;

public:
	LanguageModel(const std::string& filename, int order) : model(vocab, order)
	{
		File file(filename.c_str(), "r");
		model.read(file);
	}

	LogP wordProb(const std::string& context1, const std::string& context2, const std::string& word)
	{
		const VocabIndex context[] = {
			context2 == "__" ? Vocab_None : vocab.getIndex(context2.c_str()),
			context1 == "__" ? Vocab_None : vocab.getIndex(context1.c_str())
		};

		return model.wordProb(vocab.getIndex(word.c_str()), context);
	}
};


BOOST_PYTHON_MODULE(srilmcc)
{
	class_<LanguageModel, boost::noncopyable>("LanguageModel", init<const std::string&, int>())
		.def("wordProb", &LanguageModel::wordProb)
	;
}
