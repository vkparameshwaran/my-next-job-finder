import { useDropzone } from "react-dropzone";
import clsx from "clsx";

interface Props {
  onFile: (file: File) => void;
  file: File | null;
}

export default function Dropzone({ onFile, file }: Props) {
  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    accept: {
      "application/pdf": [".pdf"],
      "application/vnd.openxmlformats-officedocument.wordprocessingml.document": [".docx"],
    },
    maxFiles: 1,
    onDrop: (accepted) => {
      const first = accepted[0];
      if (first) onFile(first);
    },
  });

  return (
    <div
      {...getRootProps()}
      className={clsx(
        "border-2 border-dashed rounded-lg p-10 text-center cursor-pointer transition",
        isDragActive
          ? "border-blue-500 bg-blue-50"
          : "border-slate-300 bg-white hover:border-slate-400",
      )}
    >
      <input {...getInputProps()} />
      {file ? (
        <div>
          <p className="font-medium text-slate-900">{file.name}</p>
          <p className="text-sm text-slate-500 mt-1">
            {(file.size / 1024).toFixed(1)} KB — click to replace
          </p>
        </div>
      ) : (
        <div>
          <p className="font-medium text-slate-900">
            {isDragActive ? "Drop the resume here" : "Drag a resume PDF or DOCX here"}
          </p>
          <p className="text-sm text-slate-500 mt-1">or click to browse</p>
        </div>
      )}
    </div>
  );
}
