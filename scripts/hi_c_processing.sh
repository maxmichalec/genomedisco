####
# Based on ../paper_analysis/2017-12-20/2017-12-20.analysis.sh
####

step=$1
resolution=50000
DATA=/users/mmich/project/genomedisco/data
MYCODE=/users/mmich/project/genomedisco
CELL=IMR90

if [[ ${step} == "process" ]];
then
    mkdir -p ${DATA}/Rao_data/hic/res${resolution}
    for f in $(ls ${DATA}/${CELL}/*hic);
    do
        s=${DATA}/Rao_data/hic/split_$(basename ${f}).sh
        echo "" > ${s}
        # for chromo in $(echo "1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,X" | sed 's/,/ /g');
        for chromo in $(echo "21,22" | sed 's/,/ /g');
        do
            out=${DATA}/Rao_data/hic/res${resolution}/${CELL}.$(basename ${f}).res${resolution}.chr${chromo}.gz
            echo "java -jar ${DATA}/juicer_tools.1.7.5_linux_x64_jcuda.0.8.jar dump observed NONE ${f} ${chromo} ${chromo} BP ${resolution} ${out}.f" >> ${s}
            echo "zcat -f ${out}.f | awk -v chromosome=${chromo} '{print chromosome\"\t\""'$'"1\"\t\"chromosome\"\t\""'$'"2\"\t\""'$'"3}' | gzip > ${out}" >> ${s}
            echo "rm ${out}.f" >> ${s}
        done
        chmod 755 ${s}
        $s
        echo "${f} done"
    done

    # Create combined file including all chromosomes
    #TODO: manual for now

    # for chromo in $(echo "1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,X" | sed 's/,/ /g');
    # for chromo in $(echo "21,22" | sed 's/,/ /g');
    # do
    #     echo ${chromo}
    #     zcat -f ${DATA}/Rao_data/hic/GM12878_combined/50kb_resolution_intrachromosomal/chr${chromo}/MAPQGE30/chr${chromo}_50kb.RAWobserved | awk -v chromosome=${chromo} '{print chromosome"\t"$1"\t"chromosome"\t"$2"\t"$3}' | gzip > ${DATA}/Rao_data/hic/res50000/GM12878_combined.res50000.chr${chromo}.gz
    # done

    # for cellline in GM12878_combined;
    # do
    #     echo ${cellline}
    #     zcat -f ${DATA}/Rao_data/hic/res${resolution}/*${cellline}*chr*gz | gzip > ${DATA}/Rao_data/hic/res${resolution}/${cellline}.res${resolution}.gz
    # done

    # for f in $(ls ${DATA}/Rao_data/counts/*gz);
	# do
	#     for res in $(echo ${resolutions} | sed 's/,/ /g');
    #         do 
	# 	mkdir -p ${DATA}/Rao_data/counts/res${res}
	# 	#once for the whole genome
	# 	out=${DATA}/Rao_data/counts/res${res}/$(basename ${f} | sed 's/_merged_nodups[.]txt[.]gz[.]//g' | sed 's/_/\t/g' | cut -f2).res${res}.gz
	# 	s=${out}.sh
	# 	echo ${out}
	# 	echo "${MYCODE}/genome_utils/3Dutils/LA_reads_to_n1n2value_bins.sh ${f} ${out} ${MAPQ} intra ${res}" > ${s}
	# 	echo "rm ${s}" >> ${s}
	# 	chmod 755 ${s}
	# 	qsub -o ${s}.o -e ${s}.e ${s}
	#     done
	# done
    # fi
fi

if [[ ${step} == "metadata" ]];
then
    for res in $(echo ${resolutions} | sed 's/,/ /g');
    do
	#metadata samples
	mkdir -p ${DATA}/results/metadata
	metadata_samples=${DATA}/results/metadata/metadata.samples.res${res}
	rm ${metadata_samples}
	for dataset_number in {1..83};
        do
            dataset="HIC"$(echo "00${dataset_number}" | sed 's/.*\(...\)/\1/')
	    echo "${dataset}delim${DATA}/Rao_data/counts/res${res}/${dataset}.res${res}.gz" | sed 's/delim/\t/g' >> ${metadata_samples}
	done

	#metadata pairs
	metadata_pairs=${DATA}/results/metadata/metadata.pairs.res${res}
	rm ${metadata_pairs}*
	#odds
	for data1 in $(zcat -f ${metadata_samples} | cut -f1 | sed -n 'p;n');
	do
	    for data2 in $(zcat -f ${metadata_samples} | cut -f1 | sed -n 'p;n');
	    do
		echo "${data1}delim${data2}" | sed 's/delim/\t/g' >> ${metadata_pairs}.tmp
	    done
	done
	#evens
	for data1 in $(zcat -f ${metadata_samples} | cut -f1 | sed -n 'n;p');
        do
            for data2 in $(zcat -f ${metadata_samples} | cut -f1 | sed -n 'n;p');
            do
                echo "${data1}delim${data2}" | sed 's/delim/\t/g' >> ${metadata_pairs}.tmp
            done
        done

	python3 ${MYCODE}/paper_analysis/orderpairs.py --file ${metadata_pairs}.tmp --out ${metadata_pairs}.tmp2
	cat ${metadata_pairs}.tmp2 | sort | uniq | awk '{if ($1!=$2) print $0}' > ${metadata_pairs}
	rm ${metadata_pairs}.tmp*
	echo ${metadata_pairs}
    done
fi
