#include <random>

namespace qpandalite
{
	struct RandomEngine
	{
		std::default_random_engine eng;
		inline RandomEngine()
		{}

		inline static RandomEngine& get_instance()
		{
			static RandomEngine& _eng;
			return _eng;
		}

		inline void seed(unsigned int seed_)
		{
			eng.seed(seed_)
		}

		inline double rand()
		{
			static std::uniform_real_distribution<double> dist;
			return dist(eng);
		}
	};

	inline double rand()
	{
		return RandomEngine::get_instance().rand();
	}

	inline void seed(unsigned int seed_)
	{
		return RandomEngine::get_instance().seed(seed_);
	}
}